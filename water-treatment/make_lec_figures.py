"""Model figures for the water-treatment lecture (water-treatment/lec.qmd).

Constructed teaching examples, not plant data. Stage removals, waters and doses
are round illustrative numbers; stoichiometry follows notes.qmd and exercise.qmd.
Run from the repository root:  python3 water-treatment/make_lec_figures.py
Writes SVG files to water-treatment/fig/ and prints the values quoted on slides.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "fig"
OUT.mkdir(exist_ok=True)

INK, GREY, ACCENT = "#1b2a3a", "#6b7785", "#b8860b"
BLUE, GREEN, RUST, RED = "#2468A0", "#25713E", "#AD4825", "#c0392b"
SLUDGE = "#8a6a3f"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 15,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "svg.fonttype": "none",
    "figure.dpi": 100,
})


def save(fig, name):
    fig.savefig(OUT / name, format="svg", bbox_inches="tight", transparent=True)
    plt.close(fig)


def train(m0, fractions):
    """Sequential stages: each removes a fraction of what enters it. Returns water after each stage and removals."""
    water, removed = [m0], []
    for f in fractions:
        removed.append(water[-1] * f)
        water.append(water[-1] * (1 - f))
    return water, removed


# ---------------------------------------------------------------- numbers
w, r = train(10.0, [0.60, 0.50])
print("worked example: water", w, "removed", r, "overall", 1 - w[-1] / w[0])
w1, r1 = train(100.0, [0.30, 0.30])
print("exercise 1: water", [round(x, 2) for x in w1], "overall", round(1 - w1[-1] / 100, 3))
print("coagulant: 0.0200 mmol/L Fe3+ -> H+", 3 * 0.0200, "mmol/L")
PSTAGES = [("primary settling", 0.30), ("biological uptake", 0.40), ("chemical precipitation", 0.90)]
wp, rp = train(100.0, [f for _, f in PSTAGES])
print("P train (% of influent): water", [round(x, 1) for x in wp], "removed", [round(x, 1) for x in rp])
print("per-capita P ~2 g/day x 1e6 people x 365 d =", 2 * 1e6 * 365 / 1e6, "tonnes/yr")
print("Fe3+ that uses up 0.20 meq/L:", round(0.20 / 3, 4), "mmol/L =", round(0.20 / 3 * 55.85, 2), "mg Fe/L")

# ---------------------------------------------------------------- 1 two stages, worked example
fig, ax = plt.subplots(figsize=(8.0, 4.8))
labels = ["start", "after stage 1\n(60 % of 10)", "after stage 2\n(50 % of 4)"]
water = w
solid = [0, r[0], r[0] + r[1]]
for i in range(3):
    ax.bar(i, water[i], color=BLUE, width=0.55)
    ax.bar(i, solid[i], bottom=water[i], color=SLUDGE, width=0.55)
    ax.text(i, water[i] / 2, f"{water[i]:.2f}", ha="center", va="center", color="white", fontsize=15, fontweight="bold")
    if solid[i]:
        ax.text(i, water[i] + solid[i] / 2, f"{solid[i]:.2f}", ha="center", va="center", color="white", fontsize=15, fontweight="bold")
ax.set_xticks(range(3), labels)
ax.set_ylabel("Element mass (mg)")
ax.set_ylim(0, 11.5)
ax.set_xlim(-0.5, 3.0)
ax.text(2.4, 1.0, "in water", color=BLUE, fontsize=15, fontweight="bold")
ax.text(2.4, 6.0, "in sludge", color=SLUDGE, fontsize=15, fontweight="bold")
ax.set_title("Total stays 10.0 mg; 80 % transferred, not 110 %", fontsize=16, color=INK, loc="left")
save(fig, "two-stages.svg")

# ---------------------------------------------------------------- 2 coagulant consumes alkalinity
fig, ax = plt.subplots(figsize=(6.6, 4.8))
dose = np.linspace(0, 0.12, 200)
for at0, col, lab in ((2.00, GREEN, "hard water, 2.00 meq/L"), (0.20, RED, "soft water, 0.20 meq/L")):
    y = at0 - 3 * dose
    ax.plot(dose[y >= 0], y[y >= 0], color=col, lw=3.2)
    ax.text(0.003 if at0 < 1 else 0.05, 0.28 if at0 < 1 else 1.95, lab, color=col, fontsize=15, va="center")
ax.axhline(0, color=GREY, lw=1)
ax.plot(0.02, 0.20 - 0.06, "o", ms=10, mfc="white", mec=INK, mew=2, zorder=4)
ax.annotate("0.0200 mmol/L Fe$^{3+}$\nuses 0.0600 meq/L", (0.02, 0.14), xytext=(0.03, 0.95),
            fontsize=14, color=INK, arrowprops=dict(arrowstyle="->", color=INK))
ax.plot(0.20 / 3, 0, "o", ms=10, color=RED, zorder=4)
ax.annotate("soft water's alkalinity\nis used up", (0.20 / 3, 0), xytext=(0.075, 0.5), fontsize=14, color=RED,
            arrowprops=dict(arrowstyle="->", color=RED))
ax.set_xlim(0, 0.12)
ax.set_ylim(0, 2.1)
ax.set_xlabel("Fe$^{3+}$ dose (mmol/L)")
ax.set_ylabel("Alkalinity left (meq/L)")
ax.set_title("Constructed waters: 3 H$^+$ per Fe$^{3+}$", fontsize=16, color=INK, loc="left")
save(fig, "coagulant-alkalinity.svg")

# ---------------------------------------------------------------- 3 phosphorus train (constructed)
fig, ax = plt.subplots(figsize=(9.6, 4.6))
cols = ["#b9a27a", SLUDGE, "#5e4526"]
left = 0
for (lab, f), v, c in zip(PSTAGES, rp, cols):
    ax.barh(0, v, left=left, color=c, height=0.5)
    ax.text(left + v / 2, 0, f"{v:.1f}", ha="center", va="center", color="white", fontsize=15, fontweight="bold")
    ax.text(left + v / 2, 0.38, lab.replace(" ", "\n", 1), ha="center", va="bottom", fontsize=13, color=c)
    left += v
ax.barh(0, wp[-1], left=left, color=BLUE, height=0.5)
ax.annotate(f"effluent\n{wp[-1]:.1f}", (left + wp[-1] / 2, -0.25), xytext=(left - 6, -0.75),
            fontsize=14, color=BLUE, ha="center", arrowprops=dict(arrowstyle="->", color=BLUE))
ax.set_xlim(0, 100)
ax.set_ylim(-1.0, 1.0)
ax.set_yticks([])
ax.spines["left"].set_visible(False)
ax.set_xlabel("Share of the incoming phosphorus (%)")
ax.set_title("Constructed plant: 30 %, then 40 %, then 90 % of what remains", fontsize=16, color=INK, loc="left")
save(fig, "phosphorus-train.svg")

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
