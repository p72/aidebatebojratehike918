#!/usr/bin/env bash
# VOICEVOX エンジン（Linux・CPU 版）を入れて起動する。クラウドの環境（Ubuntu）用。
#
#   bash scripts/setup_voicevox.sh            # 最新版を入れて起動
#   VOICEVOX_VERSION=0.26.0 bash scripts/setup_voicevox.sh
#
# - 入れる場所は $VOICEVOX_DIR（既定 ~/voicevox）。入っていればダウンロードは飛ばす。
# - 配布物は約1.8GB の 7z。展開に 7z（apt の 7zip）を使う。
# - 起動済みならそのまま。ログは $VOICEVOX_DIR/engine.log。
set -euo pipefail

DIR="${VOICEVOX_DIR:-$HOME/voicevox}"
URL="${VOICEVOX_URL:-http://127.0.0.1:50021}"
PORT="${URL##*:}"

if curl -sf "$URL/version" >/dev/null 2>&1; then
  echo "起動済み: $(curl -s "$URL/version")"
  exit 0
fi

if [ ! -x "$DIR/linux-cpu-x64/run" ]; then
  VER="${VOICEVOX_VERSION:-$(git ls-remote --tags --refs https://github.com/VOICEVOX/voicevox_engine \
        | awk -F/ '{print $3}' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1)}"
  echo "VOICEVOX エンジン $VER を入れる -> $DIR"
  command -v 7z >/dev/null || apt-get install -y -qq 7zip
  mkdir -p "$DIR"
  BASE="https://github.com/VOICEVOX/voicevox_engine/releases/download/$VER/voicevox_engine-linux-cpu-x64-$VER.7z"
  # 分割されている版もあるので .001 から順に、なくなるまで取る
  n=1
  while part=$(printf '%03d' $n) && curl -sfL --retry 3 -o "$DIR/engine.7z.$part" "$BASE.$part"; do
    echo "  .$part 取得"; n=$((n + 1))
  done
  rm -f "$DIR/engine.7z.$(printf '%03d' $n)"
  [ $n -gt 1 ] || { echo "ダウンロードできない: $BASE.001" >&2; exit 1; }
  (cd "$DIR" && 7z x -y -bd engine.7z.001 >/dev/null && rm -f engine.7z.*)
  chmod +x "$DIR/linux-cpu-x64/run"
fi

echo "起動中..."
nohup "$DIR/linux-cpu-x64/run" --host 127.0.0.1 --port "$PORT" >"$DIR/engine.log" 2>&1 &
for _ in $(seq 1 60); do
  if curl -sf "$URL/version" >/dev/null 2>&1; then
    echo "起動した: $(curl -s "$URL/version")"
    exit 0
  fi
  sleep 3
done
echo "起動しない。$DIR/engine.log を見る" >&2
exit 1
