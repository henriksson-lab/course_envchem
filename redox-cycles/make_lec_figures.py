"""Model figures for the redox lecture (redox-cycles/lec.qmd).

Constructed teaching illustrations, not measured data: the time series and
porewater profiles show the typical order of redox processes with schematic
shapes and relative units. Stoichiometry follows notes.qmd and exercise.qmd.
Run from the repository root:  python3 redox-cycles/make_lec_figures.py
Writes SVG files to redox-cycles/fig/ and prints the values quoted on slides.
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
PURPLE, YELLOW = "#6c4f9c", "#a08a00"

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


def sig(x, mid, w):
    return 1 / (1 + np.exp(-(x - mid) / w))


# ---------------------------------------------------------------- numbers
nh4 = 0.100
print(f"nitrification of {nh4} mmol/L NH4+: O2 {2*nh4:.3f} mmol/L = {2*nh4*32:.2f} mg/L, H+ {2*nh4:.3f} mmol/L")
no3 = 0.0800
print(f"denitrification of {no3} mmol/L NO3-: C {no3*5/4:.4f} mmol/L = {no3*5/4*12:.3f} mg C/L, N2 {no3/2:.4f} mmol/L")
print("electrons: 4 NO3- x 5 =", 4 * 5, "; 5 CH2O x 4 =", 5 * 4, "; ratio C/N =", 5 / 4)
# atom check for 4NO3- + 5CH2O + 4H+ -> 2N2 + 5CO2 + 7H2O
left = dict(N=4, O=12 + 5, C=5, H=10 + 4)
right = dict(N=4, O=10 + 7, C=5, H=14)
print("atoms left", left, "right", right, "charge", -4 + 4, "->", 0)

# ---------------------------------------------------------------- 1 constructed bottom-water time series
t = np.linspace(0, 120, 400)
o2 = 1 - sig(t, 30, 7)
no3_ = 1 - sig(t, 52, 6)
fe = sig(t, 62, 6) * (1 - 0.55 * sig(t, 95, 5))
po4 = 0.15 + 0.85 * sig(t, 64, 7)
h2s = 0.75 * sig(t, 92, 5)
fig, ax = plt.subplots(figsize=(10, 4.8))
for y, col, lab, xl, yl in ((o2, BLUE, "O$_2$", 8, 1.06), (no3_, GREEN, "NO$_3^-$", 46, 0.86), (fe, RUST, "Fe$^{2+}$", 80, 1.0),
                            (po4, ACCENT, "phosphate", 106, 1.06), (h2s, PURPLE, "H$_2$S", 111, 0.6)):
    ax.plot(t, y, color=col, lw=3.2)
    ax.text(xl, yl, lab, color=col, fontsize=16, fontweight="bold", ha="center")
for x0, x1, lab in ((0, 35, "oxic"), (35, 58, "nitrate\nreduction"), (58, 88, "iron\nreduction"), (88, 120, "sulfate\nreduction")):
    ax.axvspan(x0, x1, color=GREY, alpha=0.05 if (x0 // 10) % 2 else 0.12, lw=0)
    ax.text((x0 + x1) / 2, 1.3, lab, ha="center", va="center", fontsize=13, color=GREY)
ax.set_xlim(0, 120)
ax.set_ylim(0, 1.42)
ax.set_yticks([])
ax.set_xlabel("Days after the bottom water is cut off from the surface")
ax.set_ylabel("Relative concentration")
fig.text(0.5, -0.06, "Constructed illustration of the typical order; real basins overlap and vary.",
         ha="center", fontsize=12, color=GREY)
save(fig, "bottom-water-series.svg")

# ---------------------------------------------------------------- 2 constructed porewater profiles
z = np.linspace(0, 20, 400)
prof = [("O$_2$", BLUE, 1 - sig(z, 0.4, 0.15), 0.1),
        ("NO$_3^-$", GREEN, 0.7 * (1 - sig(z, 1.3, 0.3)), 1.9),
        ("Mn$^{2+}$", GREY, 0.6 * np.exp(-((z - 3) / 1.6) ** 2), 3.0),
        ("Fe$^{2+}$", RUST, 0.85 * np.exp(-((z - 7) / 2.5) ** 2), 7.0),
        ("H$_2$S", PURPLE, 0.9 * sig(z, 11, 1.3), 16),
        ("CH$_4$", YELLOW, 0.8 * sig(z, 16.5, 1.0), 19.3)]
fig, ax = plt.subplots(figsize=(6.6, 5.2))
for lab, col, y, zl in prof:
    ax.plot(y, z, color=col, lw=3)
    ax.text(np.interp(zl, z, y) + 0.04, zl, lab, color=col, fontsize=15, fontweight="bold", va="center")
ax.axhline(0, color=BLUE, lw=1)
ax.text(0.98, -0.6, "bottom water", ha="right", fontsize=12, color=BLUE)
ax.set_ylim(20, -1.2)
ax.set_xlim(0, 1.2)
ax.set_xticks([])
ax.set_xlabel("Relative concentration")
ax.set_ylabel("Depth in sediment (cm)")
ax.set_title("Constructed porewater profiles", fontsize=16, color=INK, loc="left")
save(fig, "porewater.svg")

# ---------------------------------------------------------------- 3 electron budget for denitrification
fig, ax = plt.subplots(figsize=(6.4, 4.6))
for i in range(4):
    ax.bar(0, 5, bottom=i * 5, color=GREEN, width=0.5, edgecolor="white", lw=2)
    ax.text(0, i * 5 + 2.5, "NO$_3^-$: +5 e$^-$", ha="center", va="center", color="white", fontsize=13)
for i in range(5):
    ax.bar(1, 4, bottom=i * 4, color=INK, width=0.5, edgecolor="white", lw=2)
    ax.text(1, i * 4 + 2, "CH$_2$O: −4 e$^-$", ha="center", va="center", color="white", fontsize=13)
ax.axhline(20, color=RED, ls="--", lw=1.5)
ax.text(0.5, 20.7, "20 e$^-$ = 20 e$^-$", ha="center", color=RED, fontsize=15, fontweight="bold")
ax.set_xticks([0, 1], ["accepted by\n4 nitrate", "donated by\n5 CH$_2$O"])
ax.set_ylabel("Electrons")
ax.set_ylim(0, 23)
save(fig, "electron-budget.svg")

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
