"""ガチ討論版の読み上げ用データと台本を作る。

  python scripts/make_tts2.py
  powershell -File scripts/build_csv.ps1 -Tsv debate2/tts_lines.tsv -Csv script2_boj_0918.csv -CharsPerMin 550

意味は変えず、読み上げソフトが読み間違えやすい表記だけを直す。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "debate2"
CHARS_PER_MIN = 550          # 超早口
GAP_SPEAKER, CARD_SEC = 0.3, 1.0

NARRATION_OPEN = (
    "2026年9月18日、日本銀行は政策金利を1.25パーセントに引き上げました。"
    "この判断は正しかったのか。今回はガチ討論です。ファクトシートは渡していません。"
    "反対するのはクロード・オーパス、賛成するのはジーピーティーシックス アストラ。"
    "それぞれが自分で調べ、本気で勝ちにいきます。スタート。"
)
NARRATION_CLOSE = (
    "討論のあと、お互いの発言をファクトチェックしました。"
    "オーパスは45件のうち7件が不正確、ジーピーティーシックス アストラは15件すべて正確でした。"
    "あなたはどちらの議論に軍配を上げますか。コメントで教えてください。"
)

SCENES = {1: "冒頭の主張", 3: "第1ラウンド", 5: "第2ラウンド", 7: "第3ラウンド",
          9: "第4ラウンド", 11: "第5ラウンド", 13: "第6ラウンド", 15: "最終弁論"}

# 各発言の要点（テロップ用。セリフではない）
TELOPS = {
    1: "8月のコアCPIは1.7%。その発表当日に利上げ",
    2: "見るべきは「これからの物価」",
    3: "日銀の見通しは「被告の証言」／中立金利の下限を超えた",
    4: "春闘5.01%という別の根拠",
    5: "5%賃上げ3年目でもCPIは1%台",
    6: "織り込み済みでも据え置けば円安に",
    7: "予想を作ったのは米財務長官",
    8: "効くのが遅いことは、遅らせる理由にならない",
    9: "外れたときの痛みは非対称。2000年と2006年の教訓",
    10: "人数で正しさは決まらない",
    11: "利上げは円安の経路を止められていない",
    12: "短観：企業の物価見通しは3年後・5年後とも2.6%",
    13: "見通しの上昇は原油高という供給ショック",
    14: "供給ショックでも波及は抑える必要がある（欧州中銀）",
    15: "反対の理由は4つ",
    16: "小幅に調整して、定着の危険を抑える",
}

ZEN = str.maketrans("０１２３４５６７８９", "0123456789")
KANJI = {"〇": "0", "一": "1", "二": "2", "三": "3", "四": "4",
         "五": "5", "六": "6", "七": "7", "八": "8", "九": "9"}


def kanji_decimal(m):
    return "".join(KANJI[c] for c in m.group(1)) + "." + "".join(KANJI[c] for c in m.group(2))


def to_spoken(text):
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)          # リンクは表示テキストだけ残す
    text = text.translate(ZEN)
    text = re.sub(r"(\d)・(\d)", r"\1.\2", text)                  # １・７ → 1.7
    text = re.sub(r"([〇一二三四五六七八九])・([〇一二三四五六七八九]+)", kanji_decimal, text)  # 〇・二五 → 0.25
    text = re.sub(r"([〇一二三四五六七八九])[％%]", lambda m: KANJI[m.group(1)] + "%", text)  # 二％ → 2%
    text = text.replace("％", "%")
    text = re.sub(r"(\d+)〜(\d+)月", r"\1月から\2月", text)        # 4〜6月期 → 4月から6月期
    for a, b in [("gpt-6-astra", "ジーピーティーシックス アストラ"), ("CPI", "シーピーアイ"),
                 ("ＣＰＩ", "シーピーアイ"), ("%", "パーセント"), ("上振れ", "うわぶれ"),
                 ("〜", "から")]:
        text = text.replace(a, b)
    # 引用符は読点にして、耳で引用の区切りが分かるようにする（句読点の隣では消すだけ）
    text = re.sub(r"(?<=[、。？！])[「『]|^[「『]", "", text)
    text = re.sub(r"[「『]", "、", text)
    text = re.sub(r"[」』](?=[、。？！]|$)", "", text)
    text = re.sub(r"[」』]", "、", text)
    return text


def main():
    turns = []
    for line in D.joinpath("log.md").read_text(encoding="utf-8").splitlines():
        speaker, text = line.split("「", 1)
        turns.append((speaker, to_spoken(text[:-1])))

    rows = [("ナレーター", NARRATION_OPEN)] + turns + [("ナレーター", NARRATION_CLOSE)]
    D.joinpath("tts_lines.tsv").write_text(
        "".join(f"{s}\t{t}\n" for s, t in rows), encoding="utf-8")

    # 台本（人が読む用）
    t = 0.0

    def stamp(sec):
        return f"{int(sec // 60)}:{int(sec % 60):02d}"

    def dur(text):
        return len(text) / CHARS_PER_MIN * 60

    total_chars = sum(len(x) for _, x in rows)
    out = [
        "# 動画台本：AI vs AI ガチ討論「9月18日の日銀利上げは正しかったのか？」\n",
        "## 基本設定\n",
        "| 項目 | 内容 |", "|---|---|",
        f"| 尺 | 約{total_chars / CHARS_PER_MIN:.1f}分（超早口・毎分{CHARS_PER_MIN}字で計算） |",
        f"| 文字数 | {total_chars:,}字（ナレーション{len(NARRATION_OPEN) + len(NARRATION_CLOSE)}字＋討論{sum(len(x) for _, x in turns):,}字） |",
        "| 話者 | ナレーター／Opus（反対派）／gpt-6-astra（賛成派） |",
        "| 読み上げ用データ | [script2_boj_0918.csv](script2_boj_0918.csv)（`話者,セリフ`、1文1行） |",
        "",
        "**間（ま）**：話者交代 0.3秒、ラウンドの切り替え 1.0秒＋ラウンド名のテロップ（読み上げない）。早口なので1本目より詰めています。\n",
        "**読み方の書き換え**：意味は変えず、表記だけ直しています。",
        "Markdown のリンクは表示テキストだけ残す、全角・漢数字の小数（１・７％、〇・二五）→ 1.7パーセント・0.25、",
        "CPI→シーピーアイ、%→パーセント、上振れ→うわぶれ、gpt-6-astra→ジーピーティーシックス アストラ、4〜6月→4月から6月、カギカッコは読点に置き換え（句読点の隣では外す）。\n",
        "---\n",
        f"## オープニング（0:00〜{stamp(dur(NARRATION_OPEN))}）\n",
        "**テロップ**：AI vs AI ガチ討論／9月18日の日銀利上げは正しかったのか？／ファクトシートなし・本気で勝ちにいく\n",
        f"**ナレーター**\n> {NARRATION_OPEN}\n",
    ]
    t = dur(NARRATION_OPEN)
    for i, (speaker, text) in enumerate(turns, 1):
        if i in SCENES:
            t += CARD_SEC
            out.append(f"## {SCENES[i]}\n")
        else:
            t += GAP_SPEAKER
        d = dur(text)
        out.append(f"**{speaker}**（{i}・{stamp(t)}〜{stamp(t + d)}）")
        out.append(f"> {text}\n")
        out.append(f"**テロップ**：{TELOPS[i]}\n")
        t += d
    t += CARD_SEC
    out += [
        f"## エンディング（{stamp(t)}〜{stamp(t + dur(NARRATION_CLOSE))}）\n",
        "**テロップ**：相互ファクトチェック　Opus 45件中 不正確7／gpt-6-astra 15件中 不正確0\n",
        f"**ナレーター**\n> {NARRATION_CLOSE}\n",
    ]
    t += dur(NARRATION_CLOSE)
    out[4] = f"| 尺 | 約{t / 60:.1f}分（超早口・毎分{CHARS_PER_MIN}字、間を含む） |"
    (ROOT / "script2_boj_0918.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{len(rows)} speeches, {total_chars} chars, {t / 60:.1f} min")


if __name__ == "__main__":
    main()
