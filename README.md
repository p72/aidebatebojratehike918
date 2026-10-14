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
| `scripts/astra.sh` | gpt-6-astra のセリフを1発言作る |
| `scripts/build_csv.ps1` | `tts_lines.tsv` から CSV を作り、尺を計算する |

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
