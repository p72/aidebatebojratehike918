param(
    [string]$Manifest = "build/sentences.tsv",
    [string]$OutDir = "build/audio",
    [double]$Rate = 1.0,
    [int]$Limit = 0
)
# Windows の OneCore 日本語音声（Haruka / Ichiro / Ayumi。Sayaka は WinRT から見えない）で、1文ずつ WAV を作る。
# OneCore 音声は System.Speech からは見えないので、WinRT の SpeechSynthesizer を使う。
# このファイルは BOM 付き UTF-8 で保存すること（PowerShell 5.1 が日本語を読めるように）。

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media.SpeechSynthesis, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.DataReader, Windows.Storage.Streams, ContentType = WindowsRuntime]

$asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
} | Select-Object -First 1

function Await($op, [Type]$type) {
    $task = $asTask.MakeGenericMethod($type).Invoke($null, @($op))
    $task.Wait() | Out-Null
    $task.Result
}

$voices = @{}
foreach ($v in [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices) {
    $voices[($v.DisplayName -replace '^Microsoft\s+', '')] = $v
}

$synth = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
$synth.Options.SpeakingRate = $Rate
$OutDir = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutDir)
New-Item -ItemType Directory -Force $OutDir | Out-Null

$rows = [System.IO.File]::ReadAllLines((Resolve-Path $Manifest), [System.Text.Encoding]::UTF8)
if ($Limit -gt 0) { $rows = $rows | Select-Object -First $Limit }
$total = 0.0
foreach ($row in $rows) {
    if (-not $row.Trim()) { continue }
    $id, $voice, $text = $row -split "`t", 3
    if (-not $voices.ContainsKey($voice)) { throw "voice not found: $voice (have: $($voices.Keys -join ', '))" }
    $synth.Voice = $voices[$voice]

    $stream = Await ($synth.SynthesizeTextToStreamAsync($text)) ([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
    $reader = New-Object Windows.Storage.Streams.DataReader($stream.GetInputStreamAt(0))
    $size = [uint32]$stream.Size
    $null = Await ($reader.LoadAsync($size)) ([uint32])
    $bytes = New-Object byte[] $size
    $reader.ReadBytes($bytes)
    $path = Join-Path $OutDir "$id.wav"
    [System.IO.File]::WriteAllBytes($path, $bytes)
    $reader.Dispose(); $stream.Dispose()

    # WAV ヘッダーから長さを出す（byte rate は 28 バイト目）
    $sec = ($bytes.Length - 44) / [BitConverter]::ToInt32($bytes, 28)
    $total += $sec
    '{0} {1,-7} {2,5:N2}s' -f $id, $voice, $sec
}
'total {0:N1}s ({1:N2} min) at rate {2}' -f $total, ($total / 60), $Rate
