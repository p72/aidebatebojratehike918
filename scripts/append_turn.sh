#!/usr/bin/env bash
# gpt-6-astra の出力（astra_turnN.txt）を、改行を外して討論ログに1行で追記する。
# usage: append_turn.sh <debate_dir> <turn_no>
set -euo pipefail
dir="$1"; n="$2"
source "$dir/topic.env"
name="${ASTRA_MODEL:-gpt-6-astra}"
printf '%s「%s」\n' "$name" "$(tr -d '\r\n' < "$dir/astra_turn${n}.txt")" >> "$dir/log.md"
