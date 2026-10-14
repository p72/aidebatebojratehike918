"""ガチ討論版の記事を、討論ログとファクトチェックの結果から組み立てる。

  python scripts/build_article2.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "debate2"

SECTIONS = {1: "冒頭の主張", 3: "第1ラウンド", 5: "第2ラウンド", 7: "第3ラウンド",
            9: "第4ラウンド", 11: "第5ラウンド", 13: "第6ラウンド", 15: "最終弁論"}

lines = D.joinpath("log.md").read_text(encoding="utf-8").splitlines()
body = []
for i, line in enumerate(lines, 1):
    if i in SECTIONS:
        body.append(f"## {SECTIONS[i]}\n")
    speaker, text = line.split("「", 1)
    body.append(f"**{speaker}**（{i}）「{text}\n")

spoken = sum(len(re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", l.split("「", 1)[1][:-1])) for l in lines)

head = (ROOT / "debate2" / "article_head.md").read_text(encoding="utf-8")
tail = (ROOT / "debate2" / "article_tail.md").read_text(encoding="utf-8")
fc_astra = D.joinpath("factcheck_by_astra.md").read_text(encoding="utf-8").strip()
fc_opus = D.joinpath("factcheck_by_opus.md").read_text(encoding="utf-8").strip()

out = (head.replace("{{CHARS}}", f"{spoken:,}")
       + "\n".join(body)
       + "\n---\n\n## 相互ファクトチェック\n\n"
       + "討論のあと、相手の発言を検証しました。判定は検証した側のものをそのまま載せています。\n\n"
       + "### Opus の発言を gpt-6-astra が検証\n\n" + fc_astra + "\n\n"
       + "### gpt-6-astra の発言を Opus が検証\n\n" + fc_opus + "\n\n"
       + tail.replace("{{CHARS}}", f"{spoken:,}"))
(ROOT / "debate2_boj_0918.md").write_text(out, encoding="utf-8")
print(f"{len(lines)} turns, {spoken} chars -> debate2_boj_0918.md")
