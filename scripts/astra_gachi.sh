#!/usr/bin/env bash
# ガチ討論版：ファクトシートを渡さず、gpt-6-astra が自分で Web 検索して反論する。
# usage: astra_gachi.sh <debate_dir> <turn_no> <phase>
# phase: opening | rebuttal | closing
set -euo pipefail
dir="$1"; n="$2"; phase="$3"
effort="${ASTRA_EFFORT:-high}"

case "$phase" in
  opening)  task="これはあなたの冒頭の主張です。直前のOpusの主張を叩きつつ、利上げ賛成の論陣を張ってください。" ;;
  rebuttal) task="直前のOpusの発言に反論してください。相手の一番強い論点を正面から潰し、相手の論理の穴や事実の誤りを突いてください。" ;;
  closing)  task="これはあなたの最終弁論です。討論全体を踏まえ、相手の主張が成り立たない理由と、利上げが正しかった理由で締めくくってください。" ;;
esac

{
cat <<EOF
あなたは「gpt-6-astra」というAIです。Claude（Opus）とAI同士の本気の討論をしています。
議題：2026年9月18日、日本銀行は政策金利を1.00%から1.25%に引き上げた。この判断は正しかったか。
あなたの立場：利上げに【賛成】。Opusは【反対】の立場です。

ルール：
- 目的は議論に勝つこと。譲歩は不要です。持てる推論を出し尽くしてください。
- ${task}
- Web 検索を自由に使って、自分で材料を集めてください。相手と情報は共有されていません。
- 検索で確かめられない数字や出来事を、事実として言わないでください。討論のあとに、相手があなたの発言をファクトチェックします。
- 日本語の話し言葉で、330〜370字。早口の読み上げ動画のセリフになるので、耳で聞いて分かる文にしてください。
- ファイルの読み書きやコマンドの実行はしないでください。
- 出力はセリフ本文だけ。名前やカギカッコ、前置き、出典の一覧は付けないでください。

EOF
echo "=== ここまでの討論ログ ==="
cat "$dir/log.md"
} | codex --search exec --skip-git-repo-check --sandbox read-only --ephemeral --color never \
      -c model_reasoning_effort="$effort" \
      -o "$dir/astra_turn${n}.txt" - > "$dir/astra_turn${n}.stdout.log" 2>&1

cat "$dir/astra_turn${n}.txt"
