#!/usr/bin/env bash
# 討論のあと、gpt-6-astra に Opus の発言をファクトチェックさせる。
# 議題は <debate_dir>/topic.env から読む。プロンプトは prompt_factcheck.sh が作る。
# usage: factcheck_astra.sh <debate_dir>
set -euo pipefail
dir="$1"
effort="${ASTRA_EFFORT:-high}"
source "$dir/topic.env"
# Codex の既定モデルは版によって変わるので、名前どおりのモデルに固定する
model="${ASTRA_MODEL:-gpt-6-astra}"

bash "$(dirname "$0")/prompt_factcheck.sh" "$dir" \
  | codex --search exec -m "$model" --skip-git-repo-check --sandbox read-only --ephemeral --color never \
      -c model_reasoning_effort="$effort" \
      -o "$dir/factcheck_by_astra.md" - > "$dir/factcheck_by_astra.stdout.log" 2>&1

cat "$dir/factcheck_by_astra.md"
