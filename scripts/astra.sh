#!/usr/bin/env bash
# 議題と立場は <debate_dir>/topic.env から読む。
# usage: astra.sh <debate_dir> <turn_no> <phase>
# phase: opening | rebuttal | closing
set -euo pipefail
dir="$1"; n="$2"; phase="$3"
source "$dir/topic.env"
# Codex の既定モデルは版によって変わるので、名前どおりのモデルに固定する
model="${ASTRA_MODEL:-gpt-6-astra}"

case "$phase" in
  opening)  task="これはあなたの冒頭の主張です。直前のOpusの主張に触れつつ、あなたの立場を打ち出してください。" ;;
  rebuttal) task="直前のOpusの発言に、具体的に反論してください。相手の論点をはぐらかさず、正面から返してください。" ;;
  closing)  task="これはあなたの最終弁論です。討論全体を踏まえ、なぜあなたの立場が正しいのかを締めくくってください。" ;;
esac

{
cat <<EOF
あなたは「gpt-6-astra」というAIです。Claude（Opus）とAI同士の討論をしています。
議題：${MOTION}
あなたの立場：${ASTRA_SIDE}。Opusは${OPUS_SIDE}の立場です。

ルール：
- ${task}
- 日本語の話し言葉で、${LENGTH}。テキスト読み上げ動画のセリフになるので、耳で聞いて分かる文にする。
- 以下のファクトシートにない数字や出来事は使わない。一般的な経済の理屈は使ってよい。
- ファイルの読み書きやコマンドの実行はしない。
- 出力はセリフ本文だけ。「gpt-6-astra「」」のカギカッコや名前、前置きは付けない。

EOF
echo "=== ファクトシート ==="
cat "$dir/facts.md"
echo
echo "=== ここまでの討論ログ ==="
cat "$dir/log.md"
} | codex exec -m "$model" --skip-git-repo-check --sandbox read-only --ephemeral --color never \
      -o "$dir/astra_turn${n}.txt" - > "$dir/astra_turn${n}.stdout.log" 2>&1

cat "$dir/astra_turn${n}.txt"
