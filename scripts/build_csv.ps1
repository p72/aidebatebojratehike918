param([string]$Tsv, [string]$Csv, [double]$CharsPerMin = 330)
# 1発言1行の TSV を、1文1行の「話者,セリフ」CSV に分割し、尺を集計する
$rows = New-Object System.Collections.Generic.List[string]
$rows.Add('話者,セリフ')
$total = 0; $i = 0
foreach ($line in [System.IO.File]::ReadAllLines($Tsv, [System.Text.Encoding]::UTF8)) {
    if (-not $line.Trim()) { continue }
    $i++
    $speaker, $text = $line -split "`t", 2
    $sentences = [regex]::Matches($text, '[^。？！]+[。？！]?') | ForEach-Object { $_.Value.Trim() } | Where-Object { $_ }
    foreach ($s in $sentences) { $rows.Add(('{0},"{1}"' -f $speaker, $s.Replace('"', '""'))) }
    $sec = [math]::Round($text.Length / $CharsPerMin * 60)
    $total += $text.Length
    '{0,2} {1,-12} {2,4}字 {3,3}秒 {4}文' -f $i, $speaker, $text.Length, $sec, @($sentences).Count
}
[System.IO.File]::WriteAllLines($Csv, $rows, (New-Object System.Text.UTF8Encoding $true))
$min = $total / $CharsPerMin
'合計 {0}字 / 約{1:N1}分（毎分{2}字）/ CSV {3}行' -f $total, $min, $CharsPerMin, ($rows.Count - 1)
