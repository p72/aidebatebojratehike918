"""9本目（相続税とマクロの資本蓄積）の画面用グラフ4枚を作る。数字は facts.md（元レポート）から。

  python debate9/make_charts.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["font.size"] = 17
OUT = Path(__file__).parent / "charts"
OUT.mkdir(exist_ok=True)
BLUE, ORANGE, GRAY, RED = "#2f6db5", "#e8892b", "#9a9a9a", "#c83c3c"
SIZE = (15, 5.1)


def finish(fig, name, note):
    fig.text(0.01, 0.01, note, fontsize=12, color="#555555")
    fig.savefig(OUT / name, dpi=130, facecolor="white")
    plt.close(fig)


# 1. マクロ：遺産税を廃止したら資本と産出はどれだけ増えるか（モデル別）
rows = [("Cagetti & De Nardi\n（政府支出を削って補填）", 2.4, 1.3),
        ("Cagetti & De Nardi\n（消費税で補填）", 2.7, 1.4),
        ("Cagetti & De Nardi\n（所得税で補填）", 0.8, 0.1),
        ("Castañeda ほか", 0.87, 0.4),
        ("De Nardi & Yang\n（資本税で補填）", 0.7, 0.3)]
fig, ax = plt.subplots(figsize=SIZE)
y = range(len(rows))[::-1]
h = 0.38
ax.barh([v + h / 2 for v in y], [r[1] for r in rows], h, color=BLUE, label="資本ストック")
ax.barh([v - h / 2 for v in y], [r[2] for r in rows], h, color=ORANGE, label="産出（GDP）")
for v, r in zip(y, rows):
    ax.text(r[1] + 0.04, v + h / 2, f"+{r[1]}%", va="center", fontsize=15)
    ax.text(r[2] + 0.04, v - h / 2, f"+{r[2]}%", va="center", fontsize=15)
ax.set_yticks(list(y), [r[0] for r in rows], fontsize=14)
ax.set_xlim(0, 3.2)
ax.set_xlabel("遺産税を廃止したときの増加率（%）")
ax.set_title("遺産税をなくしても、資本は+0.7〜2.7%、GDPは+0.1〜1.4%しか増えない（米国のモデル）", fontsize=19, loc="left")
ax.legend(loc="lower right", frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "macro.png", "出典：Cagetti & De Nardi（2009）、De Nardi & Yang（2016）ほか。区分B（モデル・シミュレーション）")

# 2. 家計の反応：ためる量より、回避のほうが大きく動く
rows = [("Kopczuk & Slemrod（米、申告データ）", 0.16, BLUE),
        ("Joulfaian（米、時系列）", 0.14, BLUE),
        ("Glogowsky（独、閾値のバンチング）", 0.1, BLUE),
        ("スウェーデン（非課税で孫へ回せる制度）", 1.53, RED)]
fig, ax = plt.subplots(figsize=SIZE)
y = list(range(len(rows)))[::-1]
ax.barh(y, [r[1] for r in rows], 0.55, color=[r[2] for r in rows])
labels = ["約0.16", "約0.14", "0.1未満", "約1.53（税収の約31%が逃げた）"]
for v, r, lab in zip(y, rows, labels):
    ax.text(r[1] + 0.03, v, lab, va="center", fontsize=16)
ax.set_yticks(y, [r[0] for r in rows], fontsize=15)
ax.set_xlim(0, 2.3)
ax.set_xlabel("税への反応の大きさ（弾力性）")
ax.set_title("資産をためる量はあまり動かない（青）。でも抜け道があると大きく動く（赤）", fontsize=19, loc="left")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "elasticity.png", "出典：Kopczuk & Slemrod（2001）、Joulfaian（2006）、Glogowsky（2021）、IFAU ワーキングペーパー（2019）")

# 3. 事業承継：ギリシャの同族企業（承継税20%のとき）
fig, ax = plt.subplots(figsize=SIZE)
cats = ["設備投資（対総資産）", "現金（対総資産）"]
before, after = [18, 18], [10, 12]
x = [0, 1.3]
w = 0.42
ax.bar([v - w / 2 for v in x], before, w, color=GRAY, label="承継の前")
ax.bar([v + w / 2 for v in x], after, w, color=RED, label="承継の後")
for v, b, a in zip(x, before, after):
    ax.text(v - w / 2, b + 0.4, f"{b}%", ha="center", fontsize=17)
    ax.text(v + w / 2, a + 0.4, f"{a}%", ha="center", fontsize=17, color=RED)
ax.text(x[0] + w / 2 + 0.25, 13, "約4割減", fontsize=22, color=RED, fontweight="bold")
ax.set_xticks(x, cats, fontsize=17)
ax.set_ylim(0, 22)
ax.set_ylabel("%")
ax.set_title("ギリシャ：承継税20%の時代、親から子へ継ぐと投資が約4割減った", fontsize=19, loc="left")
ax.legend(loc="upper right", frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "greece.png", "出典：Tsoutsoura（2015, Journal of Finance）。2002年に税率を20%→2%に下げると、親族への承継が約65%増えた")

# 4. 日本：課税割合と、相続財産の中身
fig, (a1, a2) = plt.subplots(1, 2, figsize=SIZE, gridspec_kw={"width_ratios": [1, 1.7]})
yrs, pct = ["2014年", "2015年", "2024年"], [4.4, 8.0, 10.4]
a1.bar(yrs, pct, 0.55, color=[GRAY, BLUE, BLUE])
for i, p in enumerate(pct):
    a1.text(i, p + 0.25, f"{p}%", ha="center", fontsize=17)
a1.set_ylim(0, 13)
a1.set_title("亡くなった人のうち相続税がかかる割合", fontsize=17, loc="left")
a1.spines[["top", "right"]].set_visible(False)
parts = [("現金・預貯金", 34.9, "#2f6db5"), ("土地", 30.2, "#8c6d3f"), ("有価証券", 17.8, "#e8892b"),
         ("家屋", 4.8, "#b0a080"), ("その他", 12.3, GRAY)]
left = 0
for name, v, c in parts:
    a2.barh(0, v, 0.5, left=left, color=c)
    a2.text(left + v / 2, 0, f"{name}\n{v}%" if v > 10 else "", ha="center", va="center",
            fontsize=15, color="white")
    left += v
a2.text(34.9 + 30.2 + 17.8 + 2.4, -0.36, "家屋 4.8%", ha="center", fontsize=14)
a2.set_xlim(0, 100)
a2.set_ylim(-0.6, 0.6)
a2.set_yticks([])
a2.set_xticks([])
a2.set_title("相続財産の中身（2024年分）：預金と株で半分超", fontsize=17, loc="left")
for s in a2.spines.values():
    s.set_visible(False)
fig.suptitle("日本：2015年の改正から相続税がかかる人が倍以上に。2024年分の税額は3兆2,446億円", fontsize=19, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "japan.png", "出典：国税庁「令和6年分 相続税の申告事績の概要」")
print("ok")
