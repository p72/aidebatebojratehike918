#!/usr/bin/env bash
# 討論のあと、相手（ASTRA_MODEL）にこちら側（OPUS_NAME）の発言をファクトチェックさせるプロンプトを書く。
# factcheck_astra.sh が Codex に渡すほか、Opus どうしの討論では Claude のサブエージェントに渡す。
# usage: prompt_factcheck.sh <debate_dir>
set -euo pipefail
dir="$1"
source "$dir/topic.env"
model="${ASTRA_MODEL:-gpt-6-astra}"
me="${OPUS_NAME:-Opus}"
me_full="Claude（Opus）"
[ "$me" != "Opus" ] && me_full="$me"

cat <<EOP
あなたは「${model}」というAIです。さきほど ${me_full} と、${SUBJECT}について討論しました。
これから、相手の ${me} の発言をファクトチェックしてください。

ルール：
- 対象は ${me} の発言だけです（行頭が「${me}「」の行。上から順に発言番号 1, 3, 5 … と数えます）。
- 発言に含まれる、確かめられる事実の主張（数字、日付、人名、出来事、引用）をすべて抜き出し、Web 検索で確かめてください。意見や評価、予測は対象外です。
- 判定は「正しい」「不正確」「確認できない」のどれかです。不正確なら、正しい内容を一言で書いてください。
- 討論の勝ち負けとは切り離して、公平に判定してください。相手に有利な結果でも、そのまま書いてください。
- ファイルの読み書きやコマンドの実行はしないでください。
- 出力は Markdown の表だけにしてください。列は「発言」「主張」「判定」「根拠」です。根拠には確かめた URL を入れてください。

EOP
echo "=== 討論ログ ==="
cat "$dir/log.md"
