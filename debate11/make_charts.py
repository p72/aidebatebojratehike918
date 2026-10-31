"""11本目（クルーグマンの日本経済論 1998→2014→2015）の画面用グラフ6枚を作る。

  python debate11/make_charts.py

2・5 は考え方を示す図（数字は説明用の例）。年月は facts.md と日銀の政策年表による。※印は未確認。
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["font.size"] = 17
plt.rcParams["mathtext.fontset"] = "dejavusans"
OUT = Path(__file__).parent / "charts"
OUT.mkdir(exist_ok=True)
BLUE, ORANGE, GRAY, RED, GREEN, PURPLE = "#2f6db5", "#e8892b", "#8a8a8a", "#c83c3c", "#3f8f3a", "#7a4fb0"
INK, SUB = "#222222", "#555555"
SIZE = (15, 5.1)


def finish(fig, name, note):
    fig.text(0.01, 0.012, note, fontsize=12, color=SUB)
    fig.savefig(OUT / name, dpi=130, facecolor="white")
    plt.close(fig)


def clean(ax):
    ax.spines[["top", "right"]].set_visible(False)


def card(ax, x, y, w, h, col, fc="white", lw=2.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=col, lw=lw, zorder=3))


# ─────────────────────────────────────────────
# 1. 年表：三本のテキストと日銀の政策
fig, ax = plt.subplots(figsize=SIZE)
ax.set_xlim(1995.5, 2017.5)
ax.set_ylim(0.4, 10)
ax.axis("off")
TY = 3.6
ax.annotate("", xy=(2017.3, TY), xytext=(1995.7, TY), arrowprops=dict(arrowstyle="-|>", lw=2.5, color=INK))
for yr in range(1996, 2018, 2):
    ax.plot([yr, yr], [TY - 0.15, TY + 0.15], color=INK, lw=1.5)
    ax.text(yr, TY - 0.75, str(yr), ha="center", fontsize=13, color=SUB)
boj = [(1999.1, "ゼロ金利", 0), (2001.2, "量的緩和", 1), (2006.2, "量的緩和解除", 0),
       (2013.3, "QQE（2%目標）", 1), (2014.8, "追加緩和", 0), (2016.1, "マイナス金利", 1)]
for x, lab, lv in boj:
    ax.plot(x, TY, "o", ms=9, color=GRAY, zorder=4)
    ax.plot([x, x], [TY - 0.2, TY - 1.35 - 0.75 * lv], color="#bbbbbb", lw=1, zorder=1)
    ax.text(x, TY - 1.7 - 0.75 * lv, lab, ha="center", fontsize=12.5, color=SUB)
ax.text(1995.7, 0.75, "● 日銀の主な政策", fontsize=12.5, color=GRAY)
works = [(1998.5, 1995.7, 6.6, "1998　イッツバック", "論文（ブルッキングス）",
          "流動性の罠の再来\n「信頼できる形で無責任に\nなると約束せよ」", BLUE),
         (2014.85, 2002.9, 6.6, "2014年10月末　日本に謝る", "コラム（NYT）",
          "「私も批判者の一人だった」\n西側はもっと下手だった", ORANGE),
         (2015.8, 2010.1, 7.3, "2015年10月　日本を考え直す", "ブログ（NYT）",
          "自然利子率はずっとマイナスかも\n目標は十分に高く\n＋財政の一撃", GREEN)]
for xe, xc, w, title, kind, body, col in works:
    ax.plot(xe, TY, "D", ms=15, color=col, zorder=5)
    card(ax, xc, 4.6, w, 5.2, col)
    ax.plot([xe, min(max(xe, xc + 0.3), xc + w - 0.3)], [TY + 0.2, 4.6], color=col, lw=2)
    ax.text(xc + 0.25, 9.25, title, fontsize=16, weight="bold", color=col, va="center", zorder=4)
    ax.text(xc + 0.25, 8.45, kind, fontsize=13, color=SUB, va="center", zorder=4)
    ax.text(xc + 0.25, 6.6, body, fontsize=14.5, color=INK, va="center", zorder=4, linespacing=1.45)
ax.set_title("クルーグマンの日本経済論：三本のテキストと日銀の政策", fontsize=20, loc="left", color=INK)
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "timeline.png", "テキストの要点は facts.md（各コラム・ブログの引用）による。日銀の政策は主なものだけ")

# ─────────────────────────────────────────────
# 2. 1998年の前提：自然利子率のマイナスは一時的、将来は元に戻る
import numpy as np
t = np.linspace(0, 10, 400)
rn = 1.5 - 3.5 * np.exp(-((t - 4) / 1.6) ** 2)          # 一時的に沈んで戻る自然利子率
r_nopromise = np.maximum(rn, 0)                          # π^e=0 なら実質金利は 0 で止まる（ZLB）
fig, (ax, axt) = plt.subplots(1, 2, figsize=SIZE, gridspec_kw=dict(width_ratios=[1.75, 1]))
ax.axhspan(-2.5, 0, color="#f6e3e3", alpha=0.55, zorder=0)
ax.plot(t, rn, color=BLUE, lw=4, label="自然利子率 $r^n$")
ax.plot(np.where(rn < 0, t, np.nan), np.where(rn < 0, 0, np.nan), color=RED, lw=4, ls="--", label="約束なし：$r\\geq 0$（ZLB）")
ax.fill_between(t, rn, r_nopromise, where=rn < 0, color=RED, alpha=0.12)
ax.axhline(0, color=INK, lw=1.2)
ax.axvspan(2.6, 5.4, color="#fde9c8", alpha=0.7, zorder=0)
ax.text(4, 2.75, "流動性の罠（一時的）", ha="center", fontsize=15)
ax.annotate("将来は元に戻る：$Y_{t+1}=Y^*$ が実現", xy=(8.6, 1.55), xytext=(5.6, 2.75), fontsize=14,
            arrowprops=dict(arrowstyle="->", color=BLUE, lw=2), color=BLUE)
ax.text(2.0, -1.4, "需要不足", color=RED, fontsize=14)
ax.set_xticks([0.5, 4, 9], ["過去", "罠の期間（今期）", "将来（$t+1$）"])
ax.set_ylabel("実質金利（%）")
ax.set_ylim(-2.5, 3.3)
ax.legend(loc="lower right", frameon=False, fontsize=13)
clean(ax)
axt.axis("off")
steps = [("前提", "罠は一時的。将来は完全雇用 $Y^*$ に戻る"),
         ("だから", "将来の $M^*$ を約束 → $P^*=M^*/Y^*$ ↑"),
         ("すると", "$\\pi^e$ ↑ → 今の $r=i-\\pi^e$ ↓"),
         ("財政は", "モデルでは軽く見える（リカードの\n等価定理のせい・pp.158–159）\n組み合わせには入れたい（p.179）")]
y = 0.97
for i, (h, b) in enumerate(steps):
    axt.text(0.0, y, h, fontsize=15, weight="bold", color=BLUE if i < 3 else GRAY, va="top", transform=axt.transAxes)
    axt.text(0.0, y - 0.085, b, fontsize=14.5, va="top", transform=axt.transAxes, linespacing=1.35)
    y -= 0.22
fig.suptitle("1998年の前提：自然利子率のマイナスは一時的で、将来は元に戻る", fontsize=19, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.04, 1, 0.93))
finish(fig, "premise1998.png", "左は考え方を示す図（数字は説明用）。右は Krugman (1998) の論理と財政への言及")

# ─────────────────────────────────────────────
# 3. 2014年「日本に謝る」：日本と西側のまちがいの比較
fig, ax = plt.subplots(figsize=SIZE)
ax.set_xlim(0, 15)
ax.set_ylim(0, 6.2)
ax.axis("off")
cols_x = [0.1, 2.7, 8.9]
heads = ["", "日本（1990年代〜）", "西側（2010年代）"]
hcol = [INK, RED, PURPLE]
for x, h, c in zip(cols_x, heads, hcol):
    ax.text(x + (2.9 if x > 1 else 0), 5.6, h, fontsize=18, weight="bold", color=c, ha="center" if x > 1 else "left")
rows = [("財政", "1996年以降、公共投資を急に減らし\n同時に増税", "「大きなまちがい」",
         "欧州の大規模な緊縮財政", "「ひどく破壊的」"),
        ("金融", "日銀への批判は「もっとも」", "（ただし大きな逆走はなし）",
         "欧州中央銀行の2011年の利上げ", "「日銀はここまでまちがえなかった」"),
        ("政治", "―", "",
         "米：困っている人を助ける政府への敵意\n独：南欧の救済への強い反発", "「社会の深い分断」")]
for i, (k, j1, j2, w1, w2) in enumerate(rows):
    y = 4.35 - i * 1.55
    ax.add_patch(FancyBboxPatch((0.05, y - 0.62), 14.9, 1.3, boxstyle="round,pad=0.02", fc="#f7f7f7" if i % 2 == 0 else "white",
                                ec="none", zorder=0))
    ax.text(0.25, y, k, fontsize=18, weight="bold", va="center")
    ax.text(2.8, y + 0.12, j1, fontsize=14.5, va="center", linespacing=1.3)
    ax.text(2.8, y - 0.48, j2, fontsize=13, va="center", color=RED)
    ax.text(9.0, y + 0.12, w1, fontsize=14.5, va="center", linespacing=1.3)
    ax.text(9.0, y - 0.48, w2, fontsize=13, va="center", color=PURPLE)
ax.plot([8.75, 8.75], [0.2, 5.9], color="#cccccc", lw=1.5)
ax.text(14.9, 0.0, "結び：「日本はかつて反面教師だったが、今ではほとんどお手本に見える」", fontsize=15, ha="right", weight="bold")
ax.set_title("2014年「日本に謝る」：日本が満点だったのではなく、西側がもっと下手だった", fontsize=19, loc="left")
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "apology2014.png", "カギカッコ内はコラムの要旨（facts.md）。比較の対象は、同じ「罠」に直面した西側の政策")

# ─────────────────────────────────────────────
# 4. 2014年の流れ：消費税・追加緩和・コラム・面会・延期
fig, ax = plt.subplots(figsize=SIZE)
ax.set_xlim(3.3, 13.0)
ax.set_ylim(-0.2, 9.6)
ax.axis("off")
TY = 4.6
ax.annotate("", xy=(12.9, TY), xytext=(3.4, TY), arrowprops=dict(arrowstyle="-|>", lw=2.5, color=INK))
for m in range(4, 13):
    ax.plot([m, m], [TY - 0.15, TY + 0.15], color=INK, lw=1.5)
    ax.text(m, TY - 0.7, f"{m}月", ha="center", fontsize=13, color=SUB)
ax.text(12.95, TY - 0.7, "2014年", ha="right", fontsize=13, color=SUB, weight="bold")
H = 1.45
# (時点のリスト, 箱の左端, 箱の下端, 幅, 分類, 本文, 色)
events = [([4.0], 3.4, 6.2, 2.8, "財政", "消費税 5% → 8%", RED),
          ([8.45], 5.2, 1.9, 3.3, "景気", "4〜6月期GDP、大きく落ちこむ", GRAY),
          ([10.99], 7.0, 6.2, 3.0, "金融", "日銀 追加緩和（10/31）", BLUE),
          ([10.95, 11.25], 7.9, 8.0, 5.0, "クルーグマン", "コラム「日本に謝る」→ 来日・安倍首相と面会 ※", ORANGE),
          ([11.6], 9.6, 1.9, 3.3, "財政", "消費税10%の延期を表明 ※", GREEN)]
for xs_, xl, yb, W, tag, lab, col in events:
    above = yb > TY
    for x in xs_:
        ax.plot(x, TY, "o", ms=13, color=col, zorder=5)
        xe = min(max(x, xl + 0.25), xl + W - 0.25)
        ax.plot([x, xe], [TY, yb if above else yb + H], color=col, lw=1.8, zorder=2)
    card(ax, xl, yb, W, H, col, lw=2)
    ax.text(xl + 0.15, yb + H - 0.4, tag, fontsize=12, color=col, va="center", zorder=4, weight="bold")
    ax.text(xl + 0.15, yb + 0.45, lab, fontsize=14.5, va="center", zorder=4)
ax.set_title("2014年の流れ：増税で景気が落ち、クルーグマンは「次の増税は待て」", fontsize=19, loc="left")
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "abe2014.png", "※ 面会と延期表明の時期は未確認（ジャパンタイムズは、面会が延期の判断に影響した可能性を報じた）")

# ─────────────────────────────────────────────
# 5. 2015年「日本を考え直す」：自然利子率がずっとマイナスなら → 脱出速度
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=SIZE)
t = np.linspace(0, 10, 400)
temp = 1.5 - 3.5 * np.exp(-((t - 4) / 1.6) ** 2)
perm = np.where(t < 2, 1.5, 1.5 - 3.0 * (1 - np.exp(-(t - 2) / 1.2)))
ax1.axhspan(-3.6, 0, color="#f6e3e3", alpha=0.5, zorder=0)
ax1.plot(t, temp, color=BLUE, lw=4, label="1998年の前提：一時的にマイナス")
ax1.plot(t, perm, color=RED, lw=4, label="2015年の前提：ずっとマイナスかも")
ax1.axhline(0, color=INK, lw=1.2)
ax1.text(9.9, -2.25, "将来も戻らない →「将来の約束」の足場がない", ha="right", fontsize=13, color=RED)
ax1.set_xticks([1, 5, 9], ["過去", "今期", "将来"])
ax1.set_ylabel("自然利子率 $r^n$（%）")
ax1.set_ylim(-3.6, 2.6)
ax1.set_title("前提の書きかえ（人口減少など ※）", fontsize=16)
ax1.legend(loc="lower left", frameon=False, fontsize=12.5)
clean(ax1)
# 右：脱出速度（エスケープ・ベロシティ）
tt = np.linspace(0, 10, 400)
low = 1.6 * np.sin(np.pi * np.clip(tt, 0, 6) / 6) * np.exp(-0.05 * tt)          # 中途半端：上がって落ちる
low = np.where(tt > 6, 0 + 0 * tt, low)
high = 3.2 * (1 - np.exp(-tt / 2.2))                                               # 十分に高い目標＋財政の一撃
ax2.axhspan(-0.4, 0.6, color="#eeeeee", zorder=0)
ax2.text(9.9, 0.1, "デフレ・低インフレの罠", ha="right", fontsize=13, color=SUB)
ax2.plot(tt, low, color=GRAY, lw=4, label="中途半端な目標：信じられず、落ちてくる")
ax2.plot(tt, high, color=GREEN, lw=4, label="十分に高い目標＋財政の一撃：脱出")
ax2.axhline(1.2, color=GRAY, lw=1.5, ls=":")
ax2.text(9.9, 1.35, "脱出速度（これを超えないと落ちる）", fontsize=13, color=SUB, ha="right")
ax2.set_xticks([0, 5, 10], ["今期", "", "将来"])
ax2.set_ylabel("インフレ予想（%）")
ax2.set_ylim(-0.4, 4.2)
ax2.set_title("脱出速度：目標は「十分に高く」", fontsize=16)
ax2.legend(loc="upper left", frameon=False, fontsize=13)
clean(ax2)
fig.suptitle("2015年「日本を考え直す」：人々が信じなければ、インフレは上がらない", fontsize=19, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.04, 1, 0.93))
finish(fig, "rethink2015.png", "考え方を示す図（数字は説明用）。結論：持続的な物価上昇を確実にするには、金融政策の体制転換＋財政刺激の一撃")

# ─────────────────────────────────────────────
# 6. まとめ：前提 → 結論の対応表
fig, ax = plt.subplots(figsize=SIZE)
ax.set_xlim(0, 15)
ax.set_ylim(0, 6.3)
ax.axis("off")
heads = [("1998", "イッツバック", BLUE), ("2014", "日本に謝る", ORANGE), ("2015", "日本を考え直す", GREEN)]
xs = [2.6, 6.75, 10.9]
for x, (yr, nm, c) in zip(xs, heads):
    card(ax, x, 5.25, 3.95, 0.9, c, fc=c)
    ax.text(x + 1.97, 5.7, f"{yr}　{nm}", ha="center", va="center", fontsize=16, weight="bold", color="white", zorder=4)
rows = [("前提", ["$r^n<0$ は一時的\n将来 $Y^*$ が実現", "（理論の話ではなく\n政策の比較）", "$r^n<0$ がずっと\n続くかも"]),
        ("処方箋", ["将来の $M^*$ を約束\n（年4%程度を長く ※）", "増税は待て\n（次の消費税）", "十分に高い目標\n＋財政の一撃"]),
        ("財政", ["補助役（モデルの\n仮定で軽く見える）", "1996年以降の\n削減・増税は失敗", "主役級の\n「一撃」"]),
        ("日本の評価", ["厳しく批判", "ほとんどお手本", "罠の深さを再認識"])]
for i, (k, vals) in enumerate(rows):
    y = 4.55 - i * 1.2
    if i % 2 == 0:
        ax.add_patch(FancyBboxPatch((0.05, y - 0.55), 14.9, 1.1, boxstyle="round,pad=0.02", fc="#f5f5f5", ec="none", zorder=0))
    ax.text(0.2, y, k, fontsize=17, weight="bold", va="center")
    for x, v in zip(xs, vals):
        ax.text(x + 1.97, y, v, ha="center", va="center", fontsize=14, linespacing=1.25)
for x0, x1 in [(6.55, 6.75), (10.7, 10.9)]:
    ax.annotate("", xy=(x1 + 0.05, 5.7), xytext=(x0 - 0.1, 5.7), arrowprops=dict(arrowstyle="-|>", lw=2, color=INK))
ax.set_title("変節か、一貫か：前提が変わると、処方箋も変わる", fontsize=20, loc="left")
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "summary.png", "facts.md による整理。※ 未確認")
