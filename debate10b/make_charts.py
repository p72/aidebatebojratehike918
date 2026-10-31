"""10本目・修正版（クルーグマン「It's Baaack」）の画面用グラフ6枚を作る。

  python debate10b/make_charts.py

GPT による監査（ロジック監査）と、ユーザーの指摘「将来 Y* が実現することが大事な仮定」を反映した版。
1〜3・5・6 は考え方を示す図（数字は説明用の例）。4 のマネタリーベースは監査で示された年末残高。
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["font.size"] = 17
plt.rcParams["mathtext.fontset"] = "dejavusans"
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


# 1. 流動性の罠：ZLB の下で、実質金利を下げられるのは期待インフレだけ
fig, ax = plt.subplots(figsize=SIZE)
labels = ["完全雇用に必要な実質金利\n（自然利子率 $r^n$）", "$\\pi^e=0\\%$ のとき\n$r=i-\\pi^e=0-0$", "$\\pi^e=2\\%$ のとき\n$r=i-\\pi^e=0-2$"]
vals = [-2, 0, -2]
ax.bar(labels, vals, 0.5, color=[GRAY, RED, BLUE])
ax.axhline(0, color="black", lw=1.2)
for i, v in enumerate(vals):
    ax.text(i, v - 0.25 if v < 0 else 0.15, f"{v:+d}%" if v else "0%（ZLB で止まる）", ha="center",
            va="top" if v < 0 else "bottom", fontsize=17)
ax.annotate("", xy=(1, -2), xytext=(1, -0.05), arrowprops=dict(arrowstyle="<->", color=RED, lw=2))
ax.text(1.12, -1.0, "$r-r^n=2\\%$ の\n金利ギャップ", color=RED, fontsize=16, va="center")
ax.set_ylim(-3, 1)
ax.set_ylabel("実質金利（%）")
ax.set_title("流動性の罠：名目金利がゼロ下限（ZLB）に張りつくと、$r$ を下げる経路は $\\pi^e$ だけ", fontsize=19, loc="left")
clean(ax)
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "trap.png", "考え方を示す図。フィッシャー式 $r=i-\\pi^e$。数字は説明用の例")

# 2. 無責任になる約束：一時的な M の増加は効かず、恒久的な M* のコミットメントが効く
t = list(range(0, 11))
temp = [100] * 3 + [130] * 3 + [100] * 5
perm = [100] * 3 + [130] * 8
fig, ax = plt.subplots(figsize=SIZE)
ax.plot(t, temp, color=GRAY, lw=4, label="一時的な $M$ 増加（罠を抜けたら回収と予想）→ $M^*$ 不変 → $P^*$ 不変 → 無効")
ax.plot(t, perm, color=BLUE, lw=4, ls="--", label="恒久的な $M^*$ 増加をコミット → $P^*=M^*/Y^*$ ↑ → $\\pi^e$ ↑ → $r$ ↓")
ax.axvspan(2.5, 5.5, color="#fde9c8", alpha=0.6)
ax.text(4, 136, "流動性の罠（ZLB）の期間", ha="center", fontsize=16)
ax.set_xticks([0, 4, 10], ["今期", "罠の期間", "将来（$t+1$）"])
ax.set_ylabel("貨幣供給（指数）")
ax.set_ylim(70, 145)
ax.set_title("「信頼できる形で無責任になると約束せよ」：効くのは将来の貨幣供給 $M^*$ へのコミットメント", fontsize=19, loc="left")
ax.legend(loc="lower right", frameon=False, fontsize=14)
clean(ax)
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "promise.png", "考え方を示す図（Krugman 1998 の要点：時間非整合性の問題を逆手に取る）。数字は説明用の例")

# 3. モデルのしかけ：将来 Y* が「実現する」なら、P* の約束 ＝ 名目所得 P*Y* の約束
fig, axes = plt.subplots(1, 2, figsize=SIZE)
cats = ["将来の物価 $P^*$", "将来の産出 $Y_{t+1}$", "将来の名目所得\n$P^*Y_{t+1}$"]
for ax, prod, title, col in [(axes[0], 0.0, "Krugman (1998)：$Y_{t+1}=Y^*$ が実現する（外生）", BLUE),
                             (axes[1], -6.0, "拡張：$Y_{t+1}$ は需要で内生的に決まる", RED)]:
    p = 10.0
    nom = ((1 + p / 100) * (1 + prod / 100) - 1) * 100
    vals = [p, prod, nom]
    ax.bar(cats, vals, 0.55, color=[ORANGE, col, GREEN])
    ax.axhline(0, color="black", lw=1)
    for i, v in enumerate(vals):
        txt = "±0%（$Y^*$ が実現）" if v == 0 else f"{v:+.1f}%" if i == 2 else f"{v:+.0f}%"
        ax.text(i, v + (0.5 if v >= 0 else -0.5), txt, ha="center", va="bottom" if v >= 0 else "top", fontsize=16)
    ax.set_ylim(-10, 14)
    ax.set_title(title, fontsize=17)
    ax.tick_params(axis="x", labelsize=14)
    clean(ax)
axes[1].text(2, -6.5, "1.10 × 0.94 = 1.034", ha="center", fontsize=15, color="#555555")
axes[0].set_ylabel("変化（%）")
fig.suptitle("$Y^*$ の実現が前提なら「$P^*$ の約束」＝「名目所得の約束」。$Y^*$ が未達なら名目所得は約束に届かない",
             fontsize=18, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.04, 1, 0.94))
finish(fig, "model.png", "左：原論文の仮定（将来の産出 Y* と貨幣供給 M* を一定とし P* = M*/Y*）。右：独自の拡張（例：物価+10%・産出−6%）")

# 4. 日本：マネタリーベースは約5倍、しかし2%の持続的なインフレは実現せず
fig, (ax, axt) = plt.subplots(1, 2, figsize=SIZE, gridspec_kw=dict(width_ratios=[1, 1.35]))
ax.bar(["2012年末", "2023年末"], [138, 673], 0.55, color=["#a9c4e6", BLUE])
for i, v in enumerate([138, 673]):
    ax.text(i, v + 12, f"約{v}兆円", ha="center", fontsize=17)
ax.set_ylim(0, 780)
ax.set_ylabel("マネタリーベース（兆円）")
ax.set_title("マネタリーベース：約5倍", fontsize=18)
clean(ax)
axt.axis("off")
lines = [("2013年4月 量的・質的金融緩和（QQE）", "2%の物価安定目標・ベースを2年で2倍"),
         ("結果", "2%の持続的な物価上昇は実現せず"),
         ("2022年以降のインフレ", "輸入物価・円安など供給側の要因が大きい"),
         ("読み方", "単純な「ベース数量説」への反証にはなるが、\n将来 $M^*$ のコミットメントの理論への反証ではない")]
y = 0.93
for head, body in lines:
    axt.text(0.0, y, head, fontsize=16, weight="bold", va="top", transform=axt.transAxes)
    axt.text(0.0, y - 0.09, body, fontsize=15, va="top", transform=axt.transAxes)
    y -= 0.25 if "\n" not in body else 0.3
fig.suptitle("日本：ベースを大きく増やしても、2%の持続的なインフレには届かなかった", fontsize=19, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.04, 1, 0.94))
finish(fig, "japan.png", "マネタリーベースは年末残高（監査メモの値：日本銀行の統計による）。右は整理")

# 5. 財政は補完：NGDPLT の目標経路に届かせるための需要形成
t = list(range(0, 11))
target = [100 * 1.03 ** i for i in t]
mon = [100 * 1.012 ** i for i in t]
mix = [m + (g - m) * min(1, max(0, (i - 2) / 4)) for m, g, i in zip(mon, target, t)]
fig, ax = plt.subplots(figsize=SIZE)
ax.plot(t, target, color="black", lw=2.5, ls="--", zorder=5, label="目標経路 $P_tY_t=N_t^{target}$（NGDPLT、年3%）")
ax.plot(t, mon, color=GRAY, lw=4, label="コミットメントのみ（民間需要が期待に反応しにくい場合）")
ax.plot(t, mix, color=GREEN, lw=4, label="コミットメント＋財政刺激（中銀が相殺しない場合）")
ax.fill_between(t, mon, target, color="#eeeeee")
ax.text(8.2, 116, "需要ギャップ\n（$Y^*$ 未達）", fontsize=16, color="#555555", ha="center")
ax.set_xticks([0, 5, 10], ["今期", "5年後", "10年後"])
ax.set_ylabel("名目GDP（今期＝100）")
ax.set_title("財政は代替ではなく補完：目標経路を実現する需要形成（Krugman 自身も政策の組合せを推奨）", fontsize=18, loc="left")
ax.legend(loc="upper left", frameon=False, fontsize=14)
clean(ax)
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "fiscal.png", "考え方を示す図。原論文：財政の過小評価は代表的家計とリカードの等価定理によるもの（p.159）、政策の組合せに財政刺激を（p.179）")

# 6. まとめ：三つの読み方
fig, ax = plt.subplots(figsize=SIZE)
ax.set_xlim(0, 15)
ax.set_ylim(0, 5.1)
ax.axis("off")
rows = [("単純な数量説", "今の $M$ ↑", "$P$ ↑", GRAY, "× 罠の中では $V$ が下がり、今の $M$ は眠る"),
        ("Krugman (1998)", "将来 $M^*$ をコミット", "$P^*=M^*/Y^*$ ↑\n$\\pi^e$ ↑ → $r$ ↓", BLUE, "○ 前提：将来 $Y^*$ が実現する"),
        ("拡張（つむぎ）", "名目所得経路をコミット\n（NGDPLT）", "財政で需要形成\n→ $Y^*$ の実現を支える", GREEN, "◎ 必須ではないが有力な補完")]
for i, (name, a, b, col, note) in enumerate(rows):
    y = 4.1 - i * 1.6
    ax.text(0.1, y, name, fontsize=18, va="center", weight="bold", color=col)
    for x, txt in [(3.3, a), (7.6, b)]:
        ax.add_patch(FancyBboxPatch((x, y - 0.6), 3.4, 1.2, boxstyle="round,pad=0.05", fc="white", ec=col, lw=2.5))
        ax.text(x + 1.7, y, txt, ha="center", va="center", fontsize=15)
    ax.annotate("", xy=(7.5, y), xytext=(6.8, y), arrowprops=dict(arrowstyle="->", lw=2.5, color=col))
    ax.text(11.3, y, note, fontsize=14, va="center")
ax.set_title("「It's Baaack」の三つの読み方", fontsize=20, loc="left")
fig.tight_layout(rect=(0, 0.04, 1, 1))
finish(fig, "mix.png", "考え方を示す図。拡張は原論文から自動的に導かれる結論ではなく、Y* を内生化したときに現れる追加の問題への対応")
