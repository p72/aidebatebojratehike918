"""VOICEVOX エンジンで、読み上げリスト（sentences.tsv）を1文ずつ WAV にする。tts_onecore.ps1 の Linux 版。

  python scripts/tts_voicevox.py build_debate7/sentences.tsv build_debate7_vv/audio --speed 1.4

- 読み上げリストの声の名前（Haruka・Ichiro・Ayumi）は役の名前として使い、VOICEVOX の話者に置き換える。
  既定はナレーター（Haruka）＝春日部つむぎ、こちら側（Ichiro）＝ずんだもん、相手（Ayumi）＝四国めたん。
  --cast "Ichiro=3,Ayumi=2,Haruka=8" か環境変数 VOICEVOX_CAST で変えられる（数字はスタイルID）。
- エンジンは scripts/setup_voicevox.sh で起動しておく（既定の場所は http://127.0.0.1:50021）。
- 出力先に使った話者の名前を cast.txt で残し、make_video.py が最後の画面のクレジットに使う。
- すでにある WAV は飛ばす（途中で止まっても続きから作れる）。作り直すときは --force。
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import wave
from pathlib import Path

DEFAULT_CAST = "Haruka=8,Ichiro=3,Ayumi=2"


def call(url, path, params=None, body=None):
    q = f"?{urllib.parse.urlencode(params)}" if params else ""
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url + path + q, data=data, method="GET" if path == "/speakers" else "POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", nargs="?", default="build/sentences.tsv")
    ap.add_argument("out_dir", nargs="?", default="build_vv/audio")
    ap.add_argument("--speed", type=float, default=1.2, help="話す速さ（speedScale）")
    ap.add_argument("--cast", default=os.environ.get("VOICEVOX_CAST", DEFAULT_CAST))
    ap.add_argument("--url", default=os.environ.get("VOICEVOX_URL", "http://127.0.0.1:50021"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    cast = {k.strip(): int(v) for k, v in (x.split("=") for x in a.cast.split(","))}
    styles = {st["id"]: f"{sp['name']}（{st['name']}）" if st["name"] != "ノーマル" else sp["name"]
              for sp in json.loads(call(a.url, "/speakers")) for st in sp["styles"]}
    for role, sid in cast.items():
        if sid not in styles:
            sys.exit(f"スタイルID {sid}（{role}）がエンジンにない")

    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = [r for r in Path(a.manifest).read_text(encoding="utf-8").splitlines() if r.strip()]
    if a.limit:
        rows = rows[:a.limit]

    total, used = 0.0, []
    for row in rows:
        sid_, voice, text = row.split("\t", 2)
        if voice.isdigit():   # 声の欄が数字なら、そのままスタイルID（make_manzai.py の読み上げリスト）
            sid = int(voice)
        elif voice in cast:
            sid = cast[voice]
        else:
            sys.exit(f"声 {voice} の配役がない（--cast に {voice}=ID を足す）")
        if sid not in styles:
            sys.exit(f"スタイルID {sid} がエンジンにない")
        if sid not in used:
            used.append(sid)
        path = out / f"{sid_}.wav"
        if not path.exists() or a.force:
            query = json.loads(call(a.url, "/audio_query", {"text": text, "speaker": sid}))
            query["speedScale"] = a.speed
            path.write_bytes(call(a.url, "/synthesis", {"speaker": sid}, query))
        with wave.open(str(path)) as w:
            sec = w.getnframes() / w.getframerate()
        total += sec
        print(f"{sid_} {voice:<7} {sec:5.2f}s", flush=True)

    (out / "cast.txt").write_text("・".join(styles[s] for s in used) + "\n", encoding="utf-8")
    print(f"total {total:.1f}s ({total / 60:.2f} min) at speed {a.speed}")


if __name__ == "__main__":
    main()
