#!/usr/bin/env bash
# ガチ討論版：ファクトシートを渡さず、gpt-6-astra が自分で Web 検索して反論する。
# 議題と立場は <debate_dir>/topic.env から読む。プロンプトは prompt_gachi.sh が作る。
# usage: astra_gachi.sh <debate_dir> <turn_no> <phase>
# phase: opening | rebuttal | closing
set -euo pipefail
dir="$1"; n="$2"; phase="$3"
effort="${ASTRA_EFFORT:-high}"
source "$dir/topic.env"
# Codex の既定モデルは版によって変わるので、名前どおりのモデルに固定する
model="${ASTRA_MODEL:-gpt-6-astra}"

bash "$(dirname "$0")/prompt_gachi.sh" "$dir" "$phase" \
  | codex --search exec -m "$model" --skip-git-repo-check --sandbox read-only --ephemeral --color never \
      -c model_reasoning_effort="$effort" \
      -o "$dir/astra_turn${n}.txt" - > "$dir/astra_turn${n}.stdout.log" 2>&1

cat "$dir/astra_turn${n}.txt"
