"""10本目（クルーグマン「It's Baaack」）の画面用グラフ6枚を作る。

  python debate10/make_charts.py

1〜3・5・6 は考え方を示す図（数字は説明用の例）。4 の日本の数字は概数（イメージ）。
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["font.size"] = 17
OUT = Path(__file__).parent / "charts"
OUT.mkdir(exist_ok=True)
BLUE, ORANGE, GRAY, RED, GREEN = "#2f6db5", "#e8892b", "#9a9a9a", "#c83c3c", "#4a9a3a"
SIZE = (15, 5.1)


def finish(fig, name, note):
    fig.text(0.01, 0.01, note, fontsize=12, color="#555555")
    fig.savefig(OUT / name, dpi=130, facecolor="white")
    plt.close(fig)


def clean(ax):
    ax.spines[["top", "right"]].set_visible(False)


# 1. 流動性の罠：名目金利は0%より下げられない
fig, ax = plt.subplots(figsize=SIZE)
labels = ["景気回復に必要な\n実質金利", "期待インフレ0%のとき\n（名目0% − 0%）", "期待インフレ+2%のとき\n（名目0% − 2%）"]
vals = [-2, 0, -2]
cols = [GRAY, RED, BLUE]
ax.bar(labels, vals, 0.5, color=cols)
ax.axhline(0, color="black", lw=1.2)
for i, v in enumerate(vals):
    ax.text(i, v - 0.25 if v < 0 else 0.15, f"{v:+d}%" if v else "0%（ここで止まる）", ha="center",
            va="top" if v < 0 else "bottom", fontsize=17)
ax.annotate("", xy=(1, -2), xytext=(1, -0.05), arrowprops=dict(arrowstyle="<->", color=RED, lw=2))
ax.text(1.12, -1.0, "2%足りない", color=RED, fontsize=17, va="center")
ax.set_ylim(-3, 1)
ax.set_ylabel("実質金利（%）")
ax.set_title("流動性の罠：名目金利が0%に張りつくと、実質金利を下げられるのは「期待インフレ」だけ", fontsize=19, loc="left")
clean(ax)
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "trap.png", "考え方を示す図。実質金利 ＝ 名目金利 − 期待インフレ率。数字は説明用の例")

# 2. 無責任になる約束：今だけ増やすお金は効かない
t = list(range(0, 11))
temp = [100] * 3 + [130] * 3 + [100] * 5
perm = [100] * 3 + [130] * 8
fig, ax = plt.subplots(figsize=SIZE)
ax.plot(t, temp, color=GRAY, lw=4, label="今だけ増やす（景気が戻ったら回収）→ 物価の予想は動かない")
ax.plot(t, perm, color=BLUE, lw=4, ls="--", label="ずっと増やしたままと約束 → 将来の物価が上がると予想される")
ax.axvspan(2.5, 5.5, color="#fde9c8", alpha=0.6)
ax.text(4, 136, "流動性の罠の間", ha="center", fontsize=16)
ax.set_xticks([0, 4, 10], ["いま", "罠の間", "将来（罠を抜けたあと）"])
ax.set_ylabel("お金の量（指数）")
ax.set_ylim(90, 145)
ax.set_title("「信頼できる形で無責任になると約束せよ」：効くのは“将来”のお金の量", fontsize=19, loc="left")
ax.legend(loc="lower right", frameon=False, fontsize=15)
clean(ax)
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "promise.png", "考え方を示す図（クルーグマン 1998「It's Baaack」の要点）。数字は説明用の例")

# 3. モデルのしかけ：将来の産出が固定なら、物価の約束＝名目所得の約束
fig, axes = plt.subplots(1, 2, figsize=SIZE)
cats = ["将来の物価", "将来の産出", "将来の名目所得\n（物価×産出）"]
for ax, prod, title, col in [(axes[0], 0, "論文のモデル：産出は外から固定", BLUE),
                             (axes[1], -6, "現実：産出は需要しだいで動く", RED)]:
    p = 10
    vals = [p, prod, p + prod]
    ax.bar(cats, vals, 0.55, color=[ORANGE, col, GREEN])
    ax.axhline(0, color="black", lw=1)
    for i, v in enumerate(vals):
        ax.text(i, v + (0.5 if v >= 0 else -0.5), f"{v:+d}%" if v else "±0%（固定）", ha="center",
                va="bottom" if v >= 0 else "top", fontsize=16)
    ax.set_ylim(-10, 14)
    ax.set_title(title, fontsize=18)
    ax.tick_params(axis="x", labelsize=14)
    clean(ax)
axes[0].set_ylabel("変化（%）")
fig.suptitle("産出が固定なら「物価の約束」と「名目所得の約束」は同じ。動くなら別もの", fontsize=19, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.04, 1, 0.94))
finish(fig, "model.png", "考え方を示す図。数字は説明用の例（物価+10%を約束した場合）")

# 4. 日本：お金は何倍にも増えたが、物価はなかなか上がらなかった（概数）
yrs = [2012, 2014, 2016, 2018, 2020, 2022, 2024]
mb = [130, 275, 400, 500, 600, 660, 670]
cpi = [-0.1, 0.5, -0.3, 0.9, -0.2, 2.3, 2.5]
fig, ax = plt.subplots(figsize=SIZE)
ax.bar(yrs, mb, 1.3, color="#a9c4e6", label="マネタリーベース（兆円・左）")
for x, v in zip(yrs, mb):
    ax.text(x, 18, f"約{v}", ha="center", fontsize=14, color="#1f3f6b")
ax.set_ylabel("兆円")
ax.set_ylim(0, 800)
ax2 = ax.twinx()
ax2.plot(yrs, cpi, color=RED, lw=4, marker="o", ms=9, label="物価上昇率（%・右）")
ax2.axhline(2, color=RED, lw=1.2, ls=":")
ax2.text(2011.2, 2.15, "目標2%", color=RED, fontsize=14)
ax2.set_ylim(-1, 4)
ax2.set_ylabel("%")
ax.set_xticks(yrs)
ax.set_title("日本：お金は約5倍に増えたのに、物価は長いあいだ2%に届かなかった", fontsize=19, loc="left")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, fontsize=15)
ax.spines[["top"]].set_visible(False)
ax2.spines[["top"]].set_visible(False)
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "japan.png", "数字は概数（イメージ）。物価は生鮮食品を除く総合、消費税の影響を除いたおおよその値")

# 5. 財政は補完：名目所得の道すじを、需要で支える
t = list(range(0, 11))
target = [100 * 1.03 ** i for i in t]
mon = [100 * 1.012 ** i for i in t]
mix = [m + (g - m) * min(1, max(0, (i - 2) / 4)) for m, g, i in zip(mon, target, t)]
fig, ax = plt.subplots(figsize=SIZE)
ax.plot(t, target, color="black", lw=2.5, ls="--", zorder=5, label="約束した名目所得の道すじ（年3%）")
ax.plot(t, mon, color=GRAY, lw=4, label="約束だけ（需要が足りず届かない）")
ax.plot(t, mix, color=GREEN, lw=4, label="約束＋財政で需要をつくる")
ax.fill_between(t, mon, target, color="#eeeeee")
ax.text(8.2, 116, "需要の\n足りない分", fontsize=16, color="#555555", ha="center")
ax.set_xticks([0, 5, 10], ["いま", "5年後", "10年後"])
ax.set_ylabel("名目所得（いま＝100）")
ax.set_title("財政は「代わり」ではなく「支え」：約束した名目所得に届かせるための需要づくり", fontsize=19, loc="left")
ax.legend(loc="upper left", frameon=False, fontsize=15)
clean(ax)
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "fiscal.png", "考え方を示す図。数字は説明用の例")

# 6. まとめ：三つの読み方
fig, ax = plt.subplots(figsize=SIZE)
ax.set_xlim(0, 15)
ax.set_ylim(0, 5.1)
ax.axis("off")
rows = [("貨幣数量説の読み", "お金を増やす", "物価が上がる", GRAY, "× 罠の中では、今のお金は眠るだけ"),
        ("論文の本筋", "将来のお金を約束", "期待インフレ↑\n実質金利↓", BLUE, "○ ただし産出は固定の仮定"),
        ("つむぎの読み", "将来の名目所得を約束", "財政で需要をつくり\n約束を本物に", GREEN, "◎ 金融と財政は補い合う")]
for i, (name, a, b, col, note) in enumerate(rows):
    y = 4.1 - i * 1.6
    ax.text(0.1, y, name, fontsize=18, va="center", weight="bold", color=col)
    for x, txt in [(3.3, a), (7.6, b)]:
        ax.add_patch(FancyBboxPatch((x, y - 0.55), 3.4, 1.1, boxstyle="round,pad=0.05", fc="white", ec=col, lw=2.5))
        ax.text(x + 1.7, y, txt, ha="center", va="center", fontsize=16)
    ax.annotate("", xy=(7.5, y), xytext=(6.8, y), arrowprops=dict(arrowstyle="->", lw=2.5, color=col))
    ax.text(11.3, y, note, fontsize=15, va="center")
ax.set_title("「It's Baaack」の三つの読み方", fontsize=20, loc="left")
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "mix.png", "考え方を示す図")
