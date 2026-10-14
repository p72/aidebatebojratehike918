"""ガチ討論版の読み上げ用データと台本を、討論フォルダの log.md と topic.env から作る。

  python scripts/make_tts.py debate2
  powershell -File scripts/build_csv.ps1 -Tsv debate2/tts_lines.tsv -Csv script2_boj_0918.csv -CharsPerMin 550

意味は変えず、読み上げソフトが読み間違えやすい表記だけを直す。
議題ごとの読み方は、討論フォルダの readings.tsv（表記<TAB>読み）に書く。
"""
import re
import sys

from topic import ROOT, load, read_log, scene_names

CHARS_PER_MIN = 550          # 超早口
GAP_SPEAKER, CARD_SEC = 0.3, 1.0

ZEN = str.maketrans("０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ",
                    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")   # 全角の数字と英大文字は半角に
KANJI = {"〇": "0", "一": "1", "二": "2", "三": "3", "四": "4",
         "五": "5", "六": "6", "七": "7", "八": "8", "九": "9"}

# どの議題でも使う読み方（長いものから順に置き換える）
READINGS = [("CPI", "シーピーアイ"), ("IMF", "アイエムエフ"),
            ("ＣＰＩ", "シーピーアイ"), ("%", "パーセント"), ("上振れ", "うわぶれ"),
            ("〜", "から")]


def kanji_decimal(m):
    return "".join(KANJI[c] for c in m.group(1)) + "." + "".join(KANJI[c] for c in m.group(2))


def to_spoken(text, extra=()):
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)          # リンクは表示テキストだけ残す
    text = text.translate(ZEN)
    text = re.sub(r"(\d)・(\d)", r"\1.\2", text)                  # １・７ → 1.7
    text = re.sub(r"([〇一二三四五六七八九])・([〇一二三四五六七八九]+)", kanji_decimal, text)  # 〇・二五 → 0.25
    text = re.sub(r"([〇一二三四五六七八九])[％%]", lambda m: KANJI[m.group(1)] + "%", text)  # 二％ → 2%
    text = text.replace("％", "%")
    text = re.sub(r"(\d+)〜(\d+)月", r"\1月から\2月", text)        # 4〜6月期 → 4月から6月期
    for a, b in list(extra) + READINGS:
        text = text.replace(a, b)
    # 引用符は読点にして、耳で引用の区切りが分かるようにする（句読点の隣では消すだけ）
    text = re.sub(r"(?<=[、。？！])[「『]|^[「『]", "", text)
    text = re.sub(r"[「『]", "、", text)
    text = re.sub(r"[」』](?=[、。？！]|$)", "", text)
    text = re.sub(r"[」』]", "、", text)
    return text


def main(dir_name):
    T = load(dir_name)
    D = T["DIR"]
    extra = [(T["ASTRA_MODEL"], T["ASTRA_READING"])] + T["READINGS"]
    turns = [(s, to_spoken(t, extra)) for s, t in read_log(dir_name)]
    scenes = scene_names(len(turns))
    open_, close = T["NARRATION_OPEN"], T["NARRATION_CLOSE"]

    rows = [("ナレーター", open_)] + turns + [("ナレーター", close)]
    D.joinpath("tts_lines.tsv").write_text(
        "".join(f"{s}\t{t}\n" for s, t in rows), encoding="utf-8")

    # 台本（人が読む用）
    def stamp(sec):
        return f"{int(sec // 60)}:{int(sec % 60):02d}"

    def dur(text):
        return len(text) / CHARS_PER_MIN * 60

    script = T["SCRIPT"]
    total_chars = sum(len(x) for _, x in rows)
    out = [
        f"# 動画台本：{T['TITLE_KICKER'].split('　')[0]}「{T['TITLE'].replace('｜', '')}」\n",
        "## 基本設定\n",
        "| 項目 | 内容 |", "|---|---|",
        "",   # 尺（最後に入れる）
        f"| 文字数 | {total_chars:,}字（ナレーション{len(open_) + len(close)}字＋討論{sum(len(x) for _, x in turns):,}字） |",
        f"| 話者 | ナレーター／Opus（{T['OPUS_ROLE']}）／{T['ASTRA_MODEL']}（{T['ASTRA_ROLE']}） |",
        f"| 読み上げ用データ | [{script}.csv]({script}.csv)（`話者,セリフ`、1文1行） |",
        "",
        "**間（ま）**：話者交代 0.3秒、ラウンドの切り替え 1.0秒＋ラウンド名のテロップ（読み上げない）。早口なので1本目より詰めています。\n",
        "**読み方の書き換え**：意味は変えず、表記だけ直しています。",
        "Markdown のリンクは表示テキストだけ残す、全角・漢数字の小数（１・７％、〇・二五）→ 1.7パーセント・0.25、",
        "CPI→シーピーアイ、%→パーセント、上振れ→うわぶれ、4〜6月→4月から6月、"
        + "".join(f"{a}→{b}、" for a, b in extra)
        + "カギカッコは読点に置き換え（句読点の隣では外す）。\n",
        "---\n",
        f"## オープニング（0:00〜{stamp(dur(open_))}）\n",
        f"**テロップ**：{T['TELOP_OPEN']}\n",
        f"**ナレーター**\n> {open_}\n",
    ]
    t = dur(open_)
    for i, (speaker, text) in enumerate(turns, 1):
        if i in scenes:
            t += CARD_SEC
            out.append(f"## {scenes[i]}\n")
        else:
            t += GAP_SPEAKER
        d = dur(text)
        out.append(f"**{speaker}**（{i}・{stamp(t)}〜{stamp(t + d)}）")
        out.append(f"> {text}\n")
        if i in T["TELOPS"]:
            out.append(f"**テロップ**：{T['TELOPS'][i]}\n")
        t += d
    t += CARD_SEC
    out += [
        f"## エンディング（{stamp(t)}〜{stamp(t + dur(close))}）\n",
        f"**テロップ**：{T['TELOP_END']}\n",
        f"**ナレーター**\n> {close}\n",
    ]
    t += dur(close)
    out[4] = f"| 尺 | 約{t / 60:.1f}分（超早口・毎分{CHARS_PER_MIN}字、間を含む） |"
    (ROOT / f"{script}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{len(rows)} speeches, {total_chars} chars, {t / 60:.1f} min -> {D.name}/tts_lines.tsv, {script}.md")


if __name__ == "__main__":
    main(sys.argv[1])
