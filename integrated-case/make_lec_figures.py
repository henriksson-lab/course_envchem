"""Model figures for the integrated case lecture (integrated-case/lec.qmd).

Constructed teaching catchment and constructed sediment observations from
notes.qmd; carbonate constants from carbonate-gases/reference.qmd (25 C).
Run from the repository root:  python3 integrated-case/make_lec_figures.py
Writes SVG files to integrated-case/fig/ and prints the values quoted on slides.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "fig"
OUT.mkdir(exist_ok=True)

BLUE, GREEN, RUST = "#2468A0", "#25713E", "#AD4825"
INK, GREY, ACCENT = "#1b2a3a", "#6b7785", "#b8860b"
RED = "#c0392b"
PK1, PK2, KW, KH = 6.35, 10.33, 1.0e-14, 0.034

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


AREA, WATER = 1.00e6, 5.00e8          # m2, L/year
ACID = (0.0200 + 2 * 0.0100) * AREA     # eq/year
NEUT, REF_ALK = 30000.0, 50000.0


def meq(eq_per_year, water=WATER):
    return eq_per_year / water * 1e3


# ---------------------------------------------------------------- numbers quoted on slides
resid = ACID - NEUT
print(f"acid input {ACID:.0f} eq/yr; residual {resid:.0f} eq/yr = {meq(resid):.4f} meq/L")
print(f"reference alkalinity {meq(REF_ALK):.4f} meq/L; adjusted {REF_ALK-resid:.0f} eq/yr = {meq(REF_ALK-resid):.4f} meq/L")
print(f"less neutralisation (20000): residual {meq(ACID-20000):.4f} meq/L, alkalinity {meq(REF_ALK-(ACID-20000)):.4f} meq/L")
print(f"double water: residual {meq(resid, 2*WATER):.4f} meq/L")


def open_pH(at, pco2):
    """pH of a water with carbonate alkalinity at (eq/L) in equilibrium with pco2 (atm)."""
    co2 = KH * pco2
    lo, hi = 2.0, 12.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        h = 10 ** -mid
        r1 = 10 ** (mid - PK1)
        r2 = 10 ** (mid - PK2)
        a = co2 * (r1 + 2 * r1 * r2) + KW / h - h
        lo, hi = (lo, mid) if a > at else (mid, hi)
    return 0.5 * (lo + hi)


for p in (4.2e-4, 4.2e-3):
    print(f"A_T 0.0800 meq/L, pCO2 {p:.1e} atm: pH {open_pH(0.0800e-3, p):.2f}; "
          f"A_T 0.100: pH {open_pH(0.100e-3, p):.2f}")
p_P = 0.200
print(f"0.200 mg P/L = {p_P/30.97*1000:.2f} umol/L = {p_P*94.97/30.97:.3f} mg PO4/L")
print(f"Fe 1.00 mg/L = {1.00/55.85*1000:.1f} umol/L")

# ---------------------------------------------------------------- 1 budget waterfall
fig, ax = plt.subplots(figsize=(7.0, 4.8))
ax.bar(0, ACID, color=RED, width=0.6)
ax.bar(1, NEUT, bottom=resid, color=BLUE, width=0.6)
ax.bar(2, resid, color=RED, width=0.6, alpha=0.75)
ax.plot([0.3, 0.7], [ACID, ACID], color=GREY, lw=1.2)
ax.plot([1.3, 1.7], [resid, resid], color=GREY, lw=1.2)
ax.text(0, ACID + 1000, "40 000", ha="center", fontsize=16, fontweight="bold", color=INK)
ax.text(1, resid + NEUT / 2, "− 30 000", ha="center", va="center", fontsize=16, fontweight="bold", color="white")
ax.text(2, resid + 1000, "10 000", ha="center", fontsize=16, fontweight="bold", color=INK)
ax.text(2, resid + 5500, "÷ 5.00 × 10$^8$ L/year\n= 0.0200 meq/L", ha="center", va="bottom", fontsize=13.5, color=RED)
ax.set_xticks([0, 1, 2], ["acid\ndeposited", "neutralised\nin soils", "residual\nto the lake"])
ax.set_ylabel("eq per year")
ax.set_ylim(0, 46000)
ax.set_title("Constructed catchment, 1.00 km$^2$", fontsize=14, color=GREY, loc="left")
save(fig, "budget.svg")

# ---------------------------------------------------------------- 2 reference alkalinity
fig, ax = plt.subplots(figsize=(5.8, 4.6))
vals = [meq(REF_ALK), meq(REF_ALK - resid), meq(REF_ALK - (ACID - 20000))]
labs = ["reference", "base case\n(30 000 neutralised)", "less neutralisation\n(20 000)"]
cols = [GREEN, BLUE, ACCENT]
ax.bar(range(3), vals, color=cols, width=0.58)
for i, v in enumerate(vals):
    ax.text(i, v + 0.003, f"{v:.4f}", ha="center", fontsize=15, color=INK)
ax.set_xticks(range(3), labs, fontsize=12.5)
ax.set_ylabel("Alkalinity export (meq/L)")
ax.set_ylim(0, 0.118)
ax.set_title("Flow-weighted annual values", fontsize=14, color=GREY, loc="left")
save(fig, "alkalinity-reference.svg")

# ---------------------------------------------------------------- 3 same alkalinity, different pH
pco2 = np.logspace(np.log10(2e-4), np.log10(2e-2), 200)
fig, ax = plt.subplots(figsize=(6.0, 4.6))
for at, col, lab in ((0.100e-3, GREEN, "A$_T$ = 0.100 meq/L"), (0.0800e-3, BLUE, "A$_T$ = 0.0800 meq/L")):
    ax.plot(pco2 * 1e6, [open_pH(at, p) for p in pco2], color=col, lw=3, label=lab)
for p, txt in ((4.2e-4, "air"), (4.2e-3, "10 × air\n(soil water)")):
    ax.axvline(p * 1e6, color=GREY, ls=":", lw=1.4)
    ax.text(p * 1e6 * 1.08, 5.5, txt, color=GREY, fontsize=12.5, va="bottom")
ax.set_xscale("log")
ax.set_xlabel("CO$_2$ partial pressure in equilibrium (µatm)")
ax.set_ylabel("Model pH")
ax.set_ylim(5.4, 7.6)
ax.legend(frameon=False, fontsize=13, loc="upper right")
ax.set_title("Same alkalinity, different CO$_2$: different pH", fontsize=14, color=INK, loc="left")
save(fig, "alkalinity-ph.svg")

# ---------------------------------------------------------------- 4 sensitivity to neutralisation
n = np.linspace(0, 40000, 200)
fig, ax = plt.subplots(figsize=(6.2, 4.6))
ax.plot(n / 1000, meq(REF_ALK - (ACID - n)), color=BLUE, lw=3)
ax.axhline(0, color=INK, lw=1)
for nv, lab in ((30000, "base case"), (20000, "worked example")):
    v = meq(REF_ALK - (ACID - nv))
    ax.plot(nv / 1000, v, "o", color=INK, ms=9, zorder=3)
    ax.annotate(f"{lab}: {v:.4f}", (nv / 1000, v), xytext=(-12, 14), textcoords="offset points",
                ha="right", fontsize=13, color=INK)
ax.set_xlabel("Acid neutralised in the catchment (1000 eq/year)")
ax.set_ylabel("Alkalinity export (meq/L)")
ax.set_xlim(0, 40)
ax.set_ylim(-0.005, 0.11)
ax.set_title("Every 10 000 eq/year = 0.0200 meq/L", fontsize=14, color=INK, loc="left")
save(fig, "sensitivity.svg")

# ---------------------------------------------------------------- 5 amount vs concentration (double water)
fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.2))
axes[0].bar([0, 1], [resid, resid], color=[RED, RED], width=0.55)
axes[0].set_xticks([0, 1], ["base", "double\nwater"])
axes[0].set_ylabel("Residual acid (eq/year)")
axes[0].set_ylim(0, 13000)
axes[0].set_title("Annual amount", fontsize=15, color=INK, loc="left")
for i in (0, 1):
    axes[0].text(i, resid + 300, "10 000", ha="center", fontsize=14, color=INK)
cs = [meq(resid), meq(resid, 2 * WATER)]
axes[1].bar([0, 1], cs, color=[RED, "#e39a91"], width=0.55)
axes[1].set_xticks([0, 1], ["base", "double\nwater"])
axes[1].set_ylabel("Residual acid (meq/L)")
axes[1].set_ylim(0, 0.026)
axes[1].set_title("Concentration", fontsize=15, color=INK, loc="left")
for i, v in enumerate(cs):
    axes[1].text(i, v + 0.0006, f"{v:.4f}", ha="center", fontsize=14, color=INK)
fig.tight_layout()
save(fig, "dilution.svg")

# ---------------------------------------------------------------- 6 sediment indicators
names = ["O$_2$\n(mg/L)", "filtered Fe\n(mg/L)", "filtered PO$_4$-P\n(mg P/L)"]
before = [8.0, 0.020, 0.010]
during = [0.20, 1.00, 0.200]
fig, ax = plt.subplots(figsize=(8.4, 4.6))
x = np.arange(3)
ax.bar(x - 0.18, before, width=0.34, color=BLUE, label="before: oxic")
ax.bar(x + 0.18, during, width=0.34, color=RUST, label="during O$_2$ depletion")
for xi, b, d in zip(x, ["8.0", "0.020", "0.010"], ["0.20", "1.00", "0.200"]):
    ax.text(xi - 0.18, float(b) * 1.15, b, ha="center", fontsize=13, color=INK)
    ax.text(xi + 0.18, float(d) * 1.15, d, ha="center", fontsize=13, color=INK)
for xi, b, d in zip(x, before, during):
    ax.text(xi, 25, f"× {d/b:g}", ha="center", fontsize=15, fontweight="bold",
            color=RED if d > b else BLUE)
ax.set_yscale("log")
ax.set_ylim(0.005, 50)
ax.set_xticks(x, names)
ax.set_ylabel("Concentration (log scale)")
ax.legend(frameon=False, fontsize=13, loc="center left", bbox_to_anchor=(1.0, 0.5))
ax.set_title("Water just above the sediment (constructed observations)", fontsize=14, color=GREY, loc="left")
save(fig, "sediment-indicators.svg")

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
