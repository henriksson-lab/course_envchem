"""Model figures for the organic matter lecture (aquatic-organic-matter/lec.qmd).

Constructed teaching examples, not measured data. Numbers match notes.qmd and
exercise.qmd. Optical and light parameters are round, typical-magnitude values
chosen for illustration, and are labelled as constructed on the slides.
Run from the repository root:  python3 aquatic-organic-matter/make_lec_figures.py
Writes SVG files to aquatic-organic-matter/fig/ and prints the values quoted on slides.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "fig"
OUT.mkdir(exist_ok=True)

C_BLUE, C_GREEN, C_RUST = "#2468A0", "#25713E", "#AD4825"
INK, GREY, ACCENT, RED = "#1b2a3a", "#6b7785", "#b8860b", "#c0392b"
BROWN = "#7a5230"

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


# ---------------------------------------------------------------- 1 free and bound metal (exercise 1)
fig, ax = plt.subplots(figsize=(6.4, 4.8))
for i, (name, free) in enumerate((("Water A", 0.500), ("Water B", 0.100))):
    total = 2.00
    bound = total - free
    ax.bar(i, free, color=C_RUST, width=0.55)
    ax.bar(i, bound, bottom=free, color=BROWN, alpha=0.55, width=0.55)
    ax.text(i, free / 2 if free > 0.2 else free + 0.06, f"free {free:.3f}", ha="center",
            va="center", fontsize=14, color="white" if free > 0.2 else INK)
    ax.text(i, free + bound / 2, f"bound {bound:.2f}\n({100*bound/total:.1f}%)", ha="center",
            va="center", fontsize=14, color=INK)
    print(f"{name}: bound fraction {100*bound/total:.1f}%")
ax.set_xticks([0, 1], ["Water A", "Water B"])
ax.set_ylabel("Dissolved metal (µmol/L)")
ax.set_ylim(0, 2.4)
ax.set_title("Same total, 2.00 µmol/L", fontsize=16, color=INK, loc="left")
save(fig, "om-bound-metal.svg")

# ---------------------------------------------------------------- 2 charge of acid groups versus pH
pH = np.linspace(2, 12, 400)
fig, ax = plt.subplots(figsize=(8.4, 4.6))
ax.axvspan(4.5, 8.5, color=C_GREEN, alpha=0.08, lw=0)
ax.text(6.5, 1.06, "most natural waters", ha="center", fontsize=13, color=C_GREEN)
for pka, col, lab, xy in ((4.0, C_BLUE, "carboxyl  –COOH → –COO$^-$", (4.75, 0.70)),
                           (10.0, C_RUST, "phenolic  –OH → –O$^-$", (5.6, 0.30))):
    ax.plot(pH, 1 / (1 + 10 ** (pka - pH)), color=col, lw=3)
    ax.text(*xy, lab, color=col, fontsize=14)
ax.set_xlabel("pH")
ax.set_ylabel("Fraction of groups\nthat have lost H$^+$")
ax.set_ylim(0, 1.12)
ax.set_title("Illustrative pK$_a$: carboxyl 4, phenolic 10 (real values spread)", fontsize=14,
             color=INK, loc="left")
save(fig, "om-group-charge.svg")

# ---------------------------------------------------------------- 3 absorbance spectra, same DOC
lam = np.linspace(300, 700, 300)
fig, ax = plt.subplots(figsize=(8.0, 4.6))
for a400, S, col, lab in ((6.0, 0.016, BROWN, "brown water"), (1.5, 0.018, C_BLUE, "pale water")):
    ax.plot(lam, a400 * np.exp(-S * (lam - 400)), color=col, lw=3, label=lab)
ax.axvspan(400, 500, color="#4a6fd1", alpha=0.08, lw=0)
ax.text(450, 17, "blue light", ha="center", fontsize=13, color="#4a6fd1")
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Absorption coefficient (1/m)")
ax.set_ylim(0, 25)
ax.legend(frameon=False, fontsize=14)
ax.set_title("Constructed: both waters 8 mg C/L", fontsize=15, color=INK, loc="left")
save(fig, "om-absorbance.svg")

# ---------------------------------------------------------------- 4 light versus depth
z = np.linspace(0, 16, 300)
fig, ax = plt.subplots(figsize=(7.2, 5.0))
for kd, col, lab, xy in ((0.3, C_BLUE, "clear", (22, 13.6)), (1.0, C_GREEN, "moderately coloured", (40, 7.0)),
                         (3.0, BROWN, "brown", (45, 3.4))):
    ax.plot(100 * np.exp(-kd * z), z, color=col, lw=3)
    z1 = np.log(100) / kd
    print(f"Kd {kd}: 1% light depth {z1:.1f} m")
    ax.plot(1, z1, "o", color=col, ms=9, zorder=4)
    ax.annotate(f"{lab} (K$_d$ = {kd} /m):\n1% light at {z1:.1f} m", (1, z1), xytext=xy, color=col,
                fontsize=13, va="center", arrowprops=dict(arrowstyle="-", color=col, lw=1))
ax.set_xlim(0, 100)
ax.set_ylim(16.5, 0)
ax.set_xlabel("Light remaining (% of surface)")
ax.set_ylabel("Depth (m)")
ax.set_title("Constructed lakes: I = I$_0$ e$^{-K_d z}$", fontsize=15, color=INK, loc="left")
save(fig, "om-light-depth.svg")

# ---------------------------------------------------------------- 5 oxygen budget of a sealed litre (exercise 2)
fig, ax = plt.subplots(figsize=(6.6, 4.6))
start, carbon = 9.00, 2.00
demand = carbon * 32.0 / 12.0
bars = [("O$_2$ at start", start, C_BLUE), ("demand of\n2.00 mg C", demand, RED),
        ("O$_2$ left", start - demand, C_BLUE)]
for i, (lab, v, col) in enumerate(bars):
    ax.bar(i, v, color=col, width=0.55, alpha=1 if i != 2 else 0.55)
    ax.text(i, v + 0.2, f"{v:.2f}", ha="center", fontsize=15, color=INK)
ax.set_xticks(range(3), [b[0] for b in bars])
ax.set_ylabel("mg O$_2$ per litre")
ax.set_ylim(0, 10.5)
ax.set_title("Sealed litre, no reaeration", fontsize=16, color=INK, loc="left")
save(fig, "om-oxygen-budget.svg")
print(f"exercise 2: demand {demand:.2f}, residual {start-demand:.2f}; worked example {3*32/12:.2f}")

# ---------------------------------------------------------------- 6 consumption over time versus ultimate demand
L = 4.00 * 32.0 / 12.0
k = 0.10  # per day, constructed
t = np.linspace(0, 40, 300)
fig, ax = plt.subplots(figsize=(8.0, 4.6))
ax.plot(t, L * (1 - np.exp(-k * t)), color=RED, lw=3)
ax.axhline(L, color=INK, ls="--", lw=1.5)
ax.text(39.5, L + 0.25, f"ultimate demand {L:.2f} mg O$_2$/L (4.00 mg C/L)", ha="right", fontsize=13, color=INK)
t25 = np.log(4 / 3) / k
ax.plot(t25, 0.25 * L, "o", color=INK, ms=8)
ax.annotate(f"25% oxidised:\n{0.25*L:.2f} mg O$_2$/L", (t25, 0.25 * L), xytext=(8, 1.0), fontsize=13,
            color=INK, arrowprops=dict(arrowstyle="-", color=GREY))
y5 = L * (1 - np.exp(-k * 5))
ax.plot(5, y5, "s", color=ACCENT, ms=8)
ax.annotate(f"after 5 days: {y5:.1f}", (5, y5), xytext=(12, 4.6), fontsize=13, color=ACCENT,
            arrowprops=dict(arrowstyle="-", color=ACCENT))
ax.set_xlim(0, 40)
ax.set_ylim(0, 12.5)
ax.set_xlabel("Time (days)")
ax.set_ylabel("O$_2$ consumed (mg/L)")
ax.set_title("Constructed first-order decay, rate 0.10 per day", fontsize=15, color=INK, loc="left")
save(fig, "om-demand-time.svg")
print(f"t at 25%: {t25:.1f} d; 5-day consumption {y5:.2f}; ultimate {L:.2f}")

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
