"""Model figures for the deposition lecture (deposition/lec.qmd).

All inputs are constructed teaching cases, not measured data. Values match
notes.qmd and exercise.qmd.
Run from the repository root:  python3 deposition/make_lec_figures.py
Writes SVG files to deposition/fig/ and prints the values quoted on slides.
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


# ---------------------------------------------------------------- numbers (constructed teaching catchment)
F_HNO3, F_H2SO4 = 0.0200, 0.0100          # mol m-2 yr-1
AREA, WATER = 1.00e6, 5.00e8              # m2, L/yr
eq_flux = F_HNO3 * 1 + F_H2SO4 * 2
load = eq_flux * AREA
neut = 30000.0
print(f"equivalent flux {eq_flux:.4f} eq/m2/yr; load {load:.0f} eq/yr")
print(f"before neutralisation {load / WATER * 1e3:.4f} meq/L; residual {load - neut:.0f} eq/yr -> {(load - neut) / WATER * 1e3:.4f} meq/L")
print(f"runoff depth {WATER / 1000 / AREA * 1000:.0f} mm/yr")
print("wet nitrate flux:", 0.600 * 1000 * 20.0e-6, "mol/m2/yr")
print("H+ inputs (mmol/m2):", [d * 1e-4 * 1e3 for d in (1.0, 10.0)])

# ---------------------------------------------------------------- 1 rain events
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.4))
a1.bar(["1 mm", "10 mm"], [4.0, 4.0], color=[BLUE, BLUE], width=0.55)
a1.set_ylim(0, 5.5)
a1.set_ylabel("rain pH")
a1.set_title("Same pH ...", fontsize=16, color=INK, loc="left")
for i in range(2):
    a1.text(i, 4.15, "pH 4.00", ha="center", fontsize=15, color=INK)
h = [0.100, 1.00]
bars = a2.bar(["1 mm", "10 mm"], h, color=[RUST, RUST], width=0.55)
for b, v in zip(bars, h):
    a2.text(b.get_x() + b.get_width() / 2, v + 0.03, f"{v:.2f}", ha="center", fontsize=15, color=INK)
a2.set_ylim(0, 1.25)
a2.set_ylabel("free H$^+$ delivered (mmol per m$^2$)")
a2.set_title("... ten times the H$^+$", fontsize=16, color=INK, loc="left")
for a in (a1, a2):
    a.set_xlabel("rain depth in the event")
fig.tight_layout(w_pad=3)
save(fig, "rain-events.svg")

# ---------------------------------------------------------------- 2 budget waterfall
fig, ax = plt.subplots(figsize=(10, 4.8))
steps = [("HNO$_3$\n1 eq/mol", 0, F_HNO3 * AREA, BLUE),
         ("H$_2$SO$_4$\n2 eq/mol", F_HNO3 * AREA, 2 * F_H2SO4 * AREA, BLUE),
         ("total acid\ninput", 0, load, INK),
         ("catchment\nneutralisation", load - neut, neut, GREEN),
         ("residual\nexport", 0, load - neut, RUST)]
for i, (lab, bottom, hgt, col) in enumerate(steps):
    ax.bar(i, hgt, bottom=bottom, color=col, width=0.6)
    sign = "−" if col == GREEN else ""
    ax.text(i, bottom + hgt + 900, f"{sign}{hgt:,.0f}".replace(",", " "), ha="center", fontsize=15, color=INK)
ax.plot([0.3, 0.7], [F_HNO3 * AREA] * 2, color=GREY, lw=1)
ax.plot([1.3, 2.7], [load] * 2, color=GREY, lw=1)
ax.plot([3.3, 3.7], [load - neut] * 2, color=GREY, lw=1)
ax.set_xticks(range(5), [s[0] for s in steps])
ax.set_ylabel("acid equivalents per year")
ax.set_ylim(0, 47000)
ax.text(2, -17500, "÷ 5.00 × 10$^8$ L/yr\n= 0.0800 meq/L", ha="center", fontsize=14, color=INK)
ax.text(4, -17500, "÷ 5.00 × 10$^8$ L/yr\n= 0.0200 meq/L", ha="center", fontsize=14, color=RUST)
ax.set_title("Constructed annual budget, 1.00 km$^2$ catchment", fontsize=16, color=INK, loc="left")
save(fig, "budget-waterfall.svg")

# ---------------------------------------------------------------- 3 load vs concentration
w = np.linspace(2.0e8, 1.2e9, 200)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.4))
a1.plot(w / 1e8, np.full_like(w, load), color=INK, lw=3)
a1.set_ylim(0, 50000)
a1.set_ylabel("annual acid load (eq/yr)")
a1.set_title("Load: set by deposition", fontsize=16, color=INK, loc="left")
a2.plot(w / 1e8, load / w * 1e3, color=BLUE, lw=3)
for wx, c in ((5.0e8, BLUE), (1.0e9, RUST)):
    a2.plot(wx / 1e8, load / wx * 1e3, "o", color=c, ms=10)
    a2.annotate(f"{load / wx * 1e3:.4f} meq/L", (wx / 1e8, load / wx * 1e3), xytext=(12, 10),
                textcoords="offset points", fontsize=14, color=c)
a2.set_ylim(0, 0.22)
a2.set_ylabel("equivalent concentration (meq/L)")
a2.set_title("Concentration: diluted by water", fontsize=16, color=INK, loc="left")
for a in (a1, a2):
    a.set_xlabel("annual water export (10$^8$ L/yr)")
    a.axvline(5.0, color=GREY, ls=":", lw=1.5)
fig.tight_layout(w_pad=3)
save(fig, "load-vs-concentration.svg")
print("wrote figures to", OUT)
