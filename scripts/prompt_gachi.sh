#!/usr/bin/env bash
# ガチ討論版で、相手に渡すプロンプトを標準出力に書く（議題・立場・ルール・ここまでの討論ログ）。
# astra_gachi.sh が Codex に渡すほか、Opus どうしの討論では Claude のサブエージェントにそのまま渡す。
# usage: prompt_gachi.sh <debate_dir> <phase>
# phase: opening | rebuttal | closing
set -euo pipefail
dir="$1"; phase="$2"
source "$dir/topic.env"
model="${ASTRA_MODEL:-gpt-6-astra}"
me="${OPUS_NAME:-Opus}"
me_full="Claude（Opus）"
[ "$me" != "Opus" ] && me_full="$me"

case "$phase" in
  opening)  task="これはあなたの冒頭の主張です。直前の${me}の主張を叩きつつ、あなたの立場の論陣を張ってください。" ;;
  rebuttal) task="直前の${me}の発言に反論してください。相手の一番強い論点を正面から潰し、相手の論理の穴や事実の誤りを突いてください。" ;;
  closing)  task="これはあなたの最終弁論です。討論全体を踏まえ、相手の主張が成り立たない理由と、あなたの立場が正しい理由で締めくくってください。" ;;
esac

# 考え方の是非を争う議題では、topic.env に NO_FACTCHECK=1 と書くとファクトチェックの予告を外す
fact_rule="- 検索で確かめられない数字や出来事を、事実として言わないでください。討論のあとに、相手があなたの発言をファクトチェックします。"
[ "${NO_FACTCHECK:-0}" = "1" ] && fact_rule="- これは考え方の是非をめぐる討論で、ファクトチェックはありません。数字の細かさより、理屈の筋の良さで勝負してください。"

cat <<EOP
あなたは「${model}」というAIです。${me_full}とAI同士の本気の討論をしています。
議題：${MOTION}
あなたの立場：${ASTRA_SIDE}。${me}は${OPUS_SIDE}の立場です。

ルール：
- 目的は議論に勝つこと。譲歩は不要です。持てる推論を出し尽くしてください。
- ${task}
- Web 検索を自由に使って、自分で材料を集めてください。相手と情報は共有されていません。
${fact_rule}
- 日本語の話し言葉で、${LENGTH}。早口の読み上げ動画のセリフになるので、耳で聞いて分かる文にしてください。
- ファイルの読み書きやコマンドの実行はしないでください。
- 出力はセリフ本文だけ。名前やカギカッコ、前置き、出典の一覧は付けないでください。

EOP
echo "=== ここまでの討論ログ ==="
cat "$dir/log.md"
