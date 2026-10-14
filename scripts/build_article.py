"""ガチ討論版の記事を、討論フォルダの討論ログとファクトチェックの結果から組み立てる。

  python scripts/build_article.py debate2

使うファイル（すべて討論フォルダの中）：topic.env、log.md、article_head.md、article_tail.md、
factcheck_by_astra.md、factcheck_by_opus.md。記事は topic.env の ARTICLE に書き出す。
"""
import re
import sys

from topic import ROOT, load, read_log, scene_names

T = load(sys.argv[1])
D = T["DIR"]

turns = read_log(sys.argv[1])
sections = scene_names(len(turns))
body = []
for i, (speaker, text) in enumerate(turns, 1):
    if i in sections:
        body.append(f"## {sections[i]}\n")
    body.append(f"**{speaker}**（{i}）「{text}」\n")

spoken = sum(len(re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)) for _, t in turns)

head = D.joinpath("article_head.md").read_text(encoding="utf-8")
tail = D.joinpath("article_tail.md").read_text(encoding="utf-8")
fc_astra = D.joinpath("factcheck_by_astra.md").read_text(encoding="utf-8").strip()
fc_opus = D.joinpath("factcheck_by_opus.md").read_text(encoding="utf-8").strip()

out = (head.replace("{{CHARS}}", f"{spoken:,}")
       + "\n".join(body)
       + "\n---\n\n## 相互ファクトチェック\n\n"
       + "討論のあと、相手の発言を検証しました。判定は検証した側のものをそのまま載せています。\n\n"
       + f"### Opus の発言を {T['ASTRA_MODEL']} が検証\n\n" + fc_astra + "\n\n"
       + f"### {T['ASTRA_MODEL']} の発言を Opus が検証\n\n" + fc_opus + "\n\n"
       + tail.replace("{{CHARS}}", f"{spoken:,}"))
(ROOT / T["ARTICLE"]).write_text(out, encoding="utf-8")
print(f"{len(turns)} turns, {spoken} chars -> {T['ARTICLE']}")
