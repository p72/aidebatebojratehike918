# AI vs AI 討論：9月18日の日銀利上げは正しかったのか？

Claude Opus 5.5 と gpt-6-astra（Codex CLI）に、2026年9月18日の日銀利上げ（政策金利 1.00%→1.25%、採決7対2）の是非を討論させ、記事と読み上げ動画用の台本にしたプロジェクトです。

- **Opus**（Claude Opus 5.5）：反対派。セリフは Claude が書いた
- **gpt-6-astra**（Codex CLI の既定モデル）：賛成派。セリフは Codex CLI が生成し、手を加えていない

## ファイル構成

| パス | 内容 |
|---|---|
| [debate_boj_0918.md](debate_boj_0918.md) | 記事。リード、全10発言、論点の整理、出典 |
| [script_boj_0918.md](script_boj_0918.md) | 動画台本。シーン、時間の目安、テロップ、間の指定 |
| [script_boj_0918.csv](script_boj_0918.csv) | 読み上げソフト用（`話者,セリフ`、1文1行、BOM付き UTF-8） |
| `debate/facts.md` | ファクトシート。両者に同じものを渡した |
| `debate/log.md` | 討論ログ。gpt-6-astra はこれを読んで反論する |
| `debate/astra_turn*.txt` | gpt-6-astra の生の出力（`*.stdout.log` は Codex の実行ログ） |
| `debate/tts_lines.tsv` | 読み上げ用のセリフ（1発言1行。読み方だけ直したもの） |
| [video/boj_debate_0918.mp4](video/boj_debate_0918.mp4) | 完成した動画（5分2秒、1920×1080、黒地に白文字、音声付き） |
| `video/boj_debate_0918.srt` | 動画と同じタイミングの字幕 |
| `scripts/astra.sh` | gpt-6-astra のセリフを1発言作る |
| `scripts/build_csv.ps1` | `tts_lines.tsv` から CSV を作り、尺を計算する |
| `scripts/tts_onecore.ps1` | Windows の音声で、1文ずつ WAV を作る |
| `scripts/make_video.py` | 読み上げリストの作成と、画面の作成・音声との結合 |

## 必要なもの

- Node.js と Codex CLI（`npm install -g @openai/codex`）
- ChatGPT アカウントでのログイン（`codex login`。確認は `codex login status`）
- bash（Git Bash など）と Windows PowerShell

## 作り方

### 1. ファクトシートと最初の発言を用意する
`debate/facts.md` に議題の事実を書き、`debate/log.md` に Opus の最初の発言を `Opus「…」` の形で書きます。
gpt-6-astra には、ファクトシートにない数字は使わないよう指示してあります。

### 2. gpt-6-astra の発言を作る

```bash
bash scripts/astra.sh debate 1 opening
```

- 引数は「フォルダ」「発言の番号」「段階」の順です。段階は `opening`（冒頭の主張）、`rebuttal`（反論）、`closing`（最終弁論）のどれかです。
- 結果は `debate/astra_turnN.txt` に保存され、画面にも表示されます。
- 出力を `gpt-6-astra「…」` の形で `log.md` に追記し、Opus の次の発言を書いて、これを繰り返します。今回は冒頭の主張、反論3往復、最終弁論で、計10発言にしました。

仕組み：ファクトシートと討論ログを標準入力から `codex exec` に渡しています。`--sandbox read-only --ephemeral` を付けているので、Codex はファイルを書き換えず、毎回前の会話を覚えていない状態で、討論ログだけを読んで答えます。PowerShell 5.1 から日本語を引数で渡すと文字化けするため、bash からパイプで渡しています。

### 3. 読み上げ用の CSV を作る

`debate/tts_lines.tsv` に `話者<TAB>セリフ` を1発言1行で書き、次を実行します。

```bash
powershell -File scripts/build_csv.ps1 -Tsv debate/tts_lines.tsv -Csv script_boj_0918.csv
```

発言ごとの文字数と秒数、合計の尺が表示されます。尺の計算は毎分330字が既定で、`-CharsPerMin` で変えられます。

読み上げソフトが読み間違えやすい表記は、`tts_lines.tsv` の段階で直します（意味は変えない）。

| 記事の表記 | 読み上げ用 |
|---|---|
| CPI | シーピーアイ |
| % | パーセント |
| 上振れ | うわぶれ |
| AI | エーアイ |
| gpt-6-astra | ジーピーティーシックス アストラ |

### 4. 動画を作る

ffmpeg と uv（Python）が必要です。途中のファイルは `build/` にでき、Git には入れません。

```bash
uv run --with pillow python scripts/make_video.py prepare
```
```bash
powershell -File scripts/tts_onecore.ps1 -Rate 1.23
```
```bash
uv run --with pillow python scripts/make_video.py render
```

- `prepare`：`debate/tts_lines.tsv` を1文ずつに分け、声の名前を付けた読み上げリスト（`build/sentences.tsv`）を作ります。
- `tts_onecore.ps1`：Windows の OneCore 音声で1文ずつ WAV を作ります。声はナレーター＝Haruka、Opus＝Ichiro、gpt-6-astra＝Ayumi です（Sayaka は WinRT から見えないため使えません）。`-Rate` は話す速さで、1.23 で全体が約5分になります。
- `render`：1文ごとに画面（PNG）を作り、音声と結合して `video/` に mp4 と srt を書き出します。
  - 音声合成が文の前後に付ける無音（末尾に約0.75秒）は削り、文の間は0.15秒、話者が替わるときは0.5秒にそろえます。
  - 画面の表記は読み上げ用から記事の表記に戻します（シーピーアイ→CPI など）。
  - 画面の切り替えはフレーム単位に丸めた時刻で決めるので、5分続けても音声とずれません。

場面の区切り（ラウンド名）は `make_video.py` の `SCENES` に、`tts_lines.tsv` の発言の順に書いてあります。発言の数を変えたらここも合わせてください。

## ガチ討論版（2本目）

[debate2_boj_0918.md](debate2_boj_0918.md)：ファクトシートを共有せず、両者が自分で Web を調べて本気で勝ちにいく版です。全16発言・5,784字（超早口で約10分）。最後に相互ファクトチェックが付いています。

| パス | 内容 |
|---|---|
| `debate2/log.md` | 討論ログ |
| `debate2/astra_turn*.txt` | gpt-6-astra の生の出力 |
| `debate2/opus_notes.md` | Opus の作戦メモ（gpt-6-astra には渡していない） |
| `debate2/factcheck_by_astra.md` | Opus の発言を gpt-6-astra が検証した表 |
| `debate2/factcheck_by_opus.md` | gpt-6-astra の発言を Opus が検証した表 |
| `debate2/article_head.md`、`article_tail.md` | 記事の冒頭と末尾 |
| `scripts/astra_gachi.sh` | gpt-6-astra の発言を作る（Web 検索あり、推論の強さ high） |
| `scripts/factcheck_astra.sh` | gpt-6-astra に Opus の発言を検証させる |
| `scripts/build_article2.py` | 討論ログとファクトチェックから記事を組み立てる |

```bash
bash scripts/astra_gachi.sh debate2 1 opening
```
```bash
bash scripts/factcheck_astra.sh debate2
```
```bash
python scripts/build_article2.py
```

**台本と動画（ガチ版）**

| パス | 内容 |
|---|---|
| [script2_boj_0918.md](script2_boj_0918.md) | 動画台本。発言ごとの時間の目安とテロップ |
| [script2_boj_0918.csv](script2_boj_0918.csv) | 読み上げソフト用（1文1行、207行） |
| [video/boj_debate2_0918.mp4](video/boj_debate2_0918.mp4) | 動画（10分6秒、超早口＝話す速さ2.0倍） |
| `video/boj_debate2_0918.srt` | 動画と同じタイミングの字幕 |
| [video/boj_debate2_0918_paged.mp4](video/boj_debate2_0918_paged.mp4) | 別バージョン。1画面に3〜10文（平均約6文）をまとめ、読み上げ中の文だけ黄色、ほかは白。音声と長さは同じ |
| `debate2/tts_lines.tsv` | 読み上げ用のセリフ（`make_tts2.py` が討論ログから作る） |
| `scripts/make_tts2.py` | 読み上げ用への変換と台本の作成 |

```bash
python scripts/make_tts2.py
```
```bash
uv run --with pillow python scripts/make_video.py prepare 2
```
```bash
powershell -File scripts/tts_onecore.ps1 -Manifest build2/sentences.tsv -OutDir build2/audio -Rate 2.0
```
```bash
uv run --with pillow python scripts/make_video.py render 2
```

- `make_tts2.py` は意味を変えずに表記だけ直します。リンクは表示テキストだけ残し、全角・漢数字の小数（１・７％、〇・二五）は 1.7パーセント・0.25 に、カギカッコは読点にします。
- 動画の画面には、読み上げ用ではなく討論ログの表記（記事と同じ）をそのまま出します。
- `make_video.py` の最後の引数で、1本目（`1`）とガチ版（`2`）を切り替えます。
- `render 2p` で、ガチ版のページ表示の動画を作ります。音声はガチ版と同じもの（`build2/audio`）を使うので、合成し直す必要はありません。1発言を7行に収まる単位でページに分け、最後のページが短くなりすぎないよう、文の数をならしています。

- `astra_gachi.sh` は `codex --search exec` で Web 検索をオンにし、`-c model_reasoning_effort=high` で推論の強さを指定します。強さは環境変数 `ASTRA_EFFORT` で変えられます。
- 1発言に1〜2分、ファクトチェックに5〜10分ほどかかります。

## 別の議題で使うとき

- `scripts/astra.sh` の議題と立場（「議題：…」「あなたの立場：…」の行）を書き換えます。
- `debate/` の中身を新しい議題のものに入れ替えます。前の分を残したい場合は、フォルダを分けて `astra.sh` の第1引数で指定します。

## 注意

- `scripts/build_csv.ps1` は BOM 付き UTF-8 で保存してください。BOM がないと PowerShell 5.1 が日本語を Shift_JIS として読み、エラーになります。
- 尺は毎分330字で計算した目安です。今回は全体で1,888字、約5分40秒です。読み上げ速度を1.1倍にすると約5分10秒になります。

## 出典

- [日本銀行「当面の金融政策運営について」（2026年9月18日）](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/k260918a.pdf)
- [The Japan Times](https://www.japantimes.co.jp/business/2026/09/18/economy/boj-meeting-september/)
- [CNBC](https://www.cnbc.com/2026/09/18/japan-raises-rates-30-year-high-yen-jgb.html)
- [第一生命経済研究所](https://www.dlri.co.jp/report/macro/665928.html)
- [日本経済新聞](https://www.nikkei.com/article/DGXZQOUB10B710Q6A910C2000000/)
