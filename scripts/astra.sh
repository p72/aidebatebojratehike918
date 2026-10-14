#!/usr/bin/env bash
# usage: astra.sh <debate_dir> <turn_no> <phase>
# phase: opening | rebuttal | closing
set -euo pipefail
dir="$1"; n="$2"; phase="$3"

case "$phase" in
  opening)  task="これはあなたの冒頭の主張です。直前のOpusの主張に触れつつ、利上げ賛成の立場を打ち出してください。" ;;
  rebuttal) task="直前のOpusの発言に、具体的に反論してください。相手の論点をはぐらかさず、正面から返してください。" ;;
  closing)  task="これはあなたの最終弁論です。討論全体を踏まえ、なぜ利上げが正しかったのかを締めくくってください。" ;;
esac

{
cat <<EOF
あなたは「gpt-6-astra」というAIです。Claude（Opus）とAI同士の討論をしています。
議題：2026年9月18日の日銀・植田総裁による利上げ（1.00%→1.25%）の是非。
あなたの立場：利上げに【賛成】。Opusは【反対】の立場です。

ルール：
- ${task}
- 日本語の話し言葉で、150〜180字。テキスト読み上げ動画のセリフになるので、耳で聞いて分かる文にする。
- 以下のファクトシートにない数字や出来事は使わない。一般的な経済の理屈は使ってよい。
- ファイルの読み書きやコマンドの実行はしない。
- 出力はセリフ本文だけ。「gpt-6-astra「」」のカギカッコや名前、前置きは付けない。

EOF
echo "=== ファクトシート ==="
cat "$dir/facts.md"
echo
echo "=== ここまでの討論ログ ==="
cat "$dir/log.md"
} | codex exec --skip-git-repo-check --sandbox read-only --ephemeral --color never \
      -o "$dir/astra_turn${n}.txt" - > "$dir/astra_turn${n}.stdout.log" 2>&1

cat "$dir/astra_turn${n}.txt"
