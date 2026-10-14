#!/usr/bin/env bash
# 討論のあと、gpt-6-astra に Opus の発言をファクトチェックさせる。
# 議題は <debate_dir>/topic.env から読む。
# usage: factcheck_astra.sh <debate_dir>
set -euo pipefail
dir="$1"
effort="${ASTRA_EFFORT:-high}"
source "$dir/topic.env"
# Codex の既定モデルは版によって変わるので、名前どおりのモデルに固定する
model="${ASTRA_MODEL:-gpt-6-astra}"

{
cat <<EOF
あなたは「${model}」というAIです。さきほど Claude（Opus）と、${SUBJECT}について討論しました。
これから、相手の Opus の発言をファクトチェックしてください。

ルール：
- 対象は Opus の発言だけです（行頭が「Opus「」の行。上から順に発言番号 1, 3, 5 … と数えます）。
- 発言に含まれる、確かめられる事実の主張（数字、日付、人名、出来事、引用）をすべて抜き出し、Web 検索で確かめてください。意見や評価、予測は対象外です。
- 判定は「正しい」「不正確」「確認できない」のどれかです。不正確なら、正しい内容を一言で書いてください。
- 討論の勝ち負けとは切り離して、公平に判定してください。相手に有利な結果でも、そのまま書いてください。
- ファイルの読み書きやコマンドの実行はしないでください。
- 出力は Markdown の表だけにしてください。列は「発言」「主張」「判定」「根拠」です。根拠には確かめた URL を入れてください。

EOF
echo "=== 討論ログ ==="
cat "$dir/log.md"
} | codex --search exec -m "$model" --skip-git-repo-check --sandbox read-only --ephemeral --color never \
      -c model_reasoning_effort="$effort" \
      -o "$dir/factcheck_by_astra.md" - > "$dir/factcheck_by_astra.stdout.log" 2>&1

cat "$dir/factcheck_by_astra.md"
