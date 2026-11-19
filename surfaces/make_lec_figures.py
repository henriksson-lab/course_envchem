"""Model figures for the surfaces lecture (surfaces/lec.qmd).

Constructed teaching-model predictions, not measured data. The bottle numbers
follow notes.qmd and exercise.qmd (1.00 mg solute, 1.00 L water, Kd in L/kg).
The surface-charge and sorption-edge curves are generic constructed shapes for
interpretation only.
Run from the repository root:  python3 surfaces/make_lec_figures.py
Writes SVG files to surfaces/fig/ and prints the values quoted on slides.
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
SOLID = "#a0773f"

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


def bottle(MT, Vw, Kd, ms):
    """Closed two-phase bottle: returns Cw (mg/L), water mass, sorbed mass (mg)."""
    cw = MT / (Vw + Kd * ms)
    return cw, cw * Vw, cw * Kd * ms


# ---------------------------------------------------------------- numbers
CASES = [("worked example", 100, 0.0100), ("double the solid", 100, 0.0200), ("K$_d$ falls to 10", 10, 0.0100)]
for lab, kd, ms in CASES:
    cw, w, sb = bottle(1.00, 1.00, kd, ms)
    print(f"{lab}: Cw={cw:.4f} mg/L, water {w:.4f} mg, solid {sb:.4f} mg, q={cw*kd:.2f} mg/kg")
print("Langmuir capacity 20 mg/kg x 0.0100 kg =", 20 * 0.0100, "mg")
for d_um in (100, 10, 1, 0.1, 0.01):
    print(f"sphere d={d_um} um: {6 / (2.65e6 * d_um * 1e-6):.3g} m2/g")

# ---------------------------------------------------------------- 1 surface area vs size
fig, ax = plt.subplots(figsize=(8.4, 4.8))
d = np.logspace(-8, -3.5, 200)                     # m
ssa = 6 / (2.65e6 * d)                              # m2/g, rho = 2.65 g/cm3
ax.loglog(d * 1e6, ssa, color=BLUE, lw=3.2)
marks = [(100, "fine sand"), (10, "silt"), (1, "clay-sized"), (0.1, "colloid"), (0.01, "nanoparticle")]
for du, lab in marks:
    v = 6 / (2.65e6 * du * 1e-6)
    ax.plot(du, v, "o", ms=9, mfc="white", mec=INK, mew=2, zorder=4)
    ax.annotate(f"{lab}\n{v:.2g} m²/g".replace("2.3e+02", "230"), (du, v), xytext=(10, 6), textcoords="offset points",
                fontsize=13, color=INK)
ax.axvspan(0.001, 1, color=ACCENT, alpha=0.1, lw=0)
ax.text(0.03, 0.012, "colloid range\n1 nm – 1 µm", color=ACCENT, fontsize=13, ha="center")
ax.set_xlim(0.004, 600)
ax.set_ylim(0.005, 3000)
ax.set_xlabel("Particle diameter (µm)")
ax.set_ylabel("Surface area per gram (m²/g)")
ax.set_title("Smooth mineral spheres: 10× smaller → 10× more surface", fontsize=16, color=INK, loc="left")
save(fig, "surface-area.svg")

# ---------------------------------------------------------------- 2 oxide surface charge vs pH
pKa1, pKa2 = 6.0, 10.0                     # constructed; zero charge at pH 8
pH = np.linspace(3, 12, 400)
h = 10.0 ** -pH
den = 1 + h / 10**-pKa1 + 10**-pKa2 / h
pos, neg = (h / 10**-pKa1) / den, (10**-pKa2 / h) / den
net = pos - neg
fig, ax = plt.subplots(figsize=(8.2, 4.6))
ax.axhline(0, color=GREY, lw=1)
ax.fill_between(pH, net, 0, where=net > 0, color=RED, alpha=0.15, lw=0)
ax.fill_between(pH, net, 0, where=net < 0, color=BLUE, alpha=0.15, lw=0)
ax.plot(pH, net, color=INK, lw=3.2)
ax.plot(8.0, 0, "o", ms=10, mfc="white", mec=INK, mew=2, zorder=4)
ax.annotate("zero net charge", (8.0, 0), xytext=(8.4, 0.45), fontsize=14, color=INK,
            arrowprops=dict(arrowstyle="->", color=INK))
ax.text(3.2, 0.42, ">FeOH$_2^+$ dominates:\nattracts anions\n(phosphate, arsenate)", fontsize=13, color=RED, va="top")
ax.text(3.2, -0.45, ">FeO$^-$ dominates at high pH:\nattracts cations (Cu$^{2+}$, Pb$^{2+}$)", fontsize=13, color=BLUE, va="top")
ax.set_xlim(3, 12)
ax.set_ylim(-1.05, 1.05)
ax.set_xlabel("pH")
ax.set_ylabel("Net surface charge\n(fraction of sites)")
ax.set_title("Constructed iron-oxide-like surface", fontsize=16, color=INK, loc="left")
save(fig, "surface-charge.svg")

# ---------------------------------------------------------------- 3 sorption edges
fig, ax = plt.subplots(figsize=(8.2, 4.6))
cat = 100 / (1 + 10 ** (2 * (5.5 - pH)))
an = 100 / (1 + 10 ** (1.2 * (pH - 8.5)))
ax.plot(pH, cat, color=BLUE, lw=3.2)
ax.plot(pH, an, color=RED, lw=3.2)
ax.text(6.25, 50, "metal cation\n(e.g. Pb$^{2+}$)", color=BLUE, fontsize=14, va="center")
ax.text(9.3, 50, "oxyanion\n(e.g. phosphate)", color=RED, fontsize=14, va="center")
ax.axvline(8.0, color=GREY, ls=":", lw=1.5)
ax.text(8.05, 103, "zero charge", color=GREY, fontsize=12)
ax.set_xlim(3, 12)
ax.set_ylim(0, 110)
ax.set_xlabel("pH")
ax.set_ylabel("Sorbed on the oxide (%)")
ax.set_title("Sorption edges (constructed shapes)", fontsize=16, color=INK, loc="left")
save(fig, "sorption-edges.svg")

# ---------------------------------------------------------------- 4 partition curve
fig, ax = plt.subplots(figsize=(7.2, 4.7))
ms = np.linspace(0, 0.05, 300)
for kd, col, lab in ((100, GREEN, "K$_d$ = 100 L/kg"), (10, RUST, "K$_d$ = 10 L/kg")):
    ax.plot(ms, 1 / (1 + kd * ms), color=col, lw=3.2)
    ax.text(0.0505, 1 / (1 + kd * 0.05), " " + lab, color=col, fontsize=14, va="center")
for m, c, lab in ((0.01, 0.5, "0.500"), (0.02, 1 / 3, "0.333")):
    ax.plot(m, c, "o", ms=10, mfc="white", mec=INK, mew=2, zorder=4)
    ax.annotate(f"{m:.3f} kg → {lab} mg/L", (m, c), xytext=(m + 0.004, c + 0.12), fontsize=13,
                color=INK, arrowprops=dict(arrowstyle="->", color=INK))
ax.set_xlim(0, 0.05)
ax.set_ylim(0, 1.05)
ax.set_xlabel("Dry solid in the bottle (kg)")
ax.set_ylabel("Water concentration C$_w$ (mg/L)")
ax.set_title("1.00 mg solute, 1.00 L water", fontsize=16, color=INK, loc="left")
save(fig, "partition-curve.svg")

# ---------------------------------------------------------------- 5 inventories in three bottles
fig, ax = plt.subplots(figsize=(7.6, 4.8))
for i, (lab, kd, m) in enumerate(CASES):
    cw, w, sb = bottle(1.00, 1.00, kd, m)
    ax.bar(i, w, color=BLUE, width=0.55)
    ax.bar(i, sb, bottom=w, color=SOLID, width=0.55)
    ax.text(i, w / 2, f"{w:.3f}", ha="center", va="center", color="white", fontsize=14, fontweight="bold")
    if sb > 0.15:
        ax.text(i, w + sb / 2, f"{sb:.3f}", ha="center", va="center", color="white", fontsize=14, fontweight="bold")
    else:
        ax.text(i, 1.04, f"solid {sb:.3f}", ha="center", color=SOLID, fontsize=13)
ax.set_xticks(range(3), ["worked\nexample", "double\nthe solid", "K$_d$ falls\nto 10"])
ax.set_ylabel("Solute mass (mg)")
ax.set_ylim(0, 1.15)
ax.text(2.45, 0.35, "in water", color=BLUE, fontsize=14, fontweight="bold")
ax.text(2.45, 0.75, "on solid", color=SOLID, fontsize=14, fontweight="bold")
ax.set_xlim(-0.5, 3.2)
ax.set_title("Total always 1.00 mg", fontsize=16, color=INK, loc="left")
save(fig, "inventory-bars.svg")

# ---------------------------------------------------------------- 6 linear vs Langmuir isotherm
fig, ax = plt.subplots(figsize=(7.4, 4.7))
c = np.linspace(0, 2.0, 300)
qmax, b = 20.0, 5.0                      # mg/kg, L/mg; initial slope qmax*b = 100 L/kg
ax.plot(c, 100 * c, color=GREY, lw=2.5, ls="--")
ax.plot(c, qmax * b * c / (1 + b * c), color=GREEN, lw=3.2)
ax.axhline(qmax, color=GREEN, ls=":", lw=1.5)
ax.text(1.98, qmax + 1.2, "q$_{max}$ = 20 mg/kg", color=GREEN, fontsize=14, ha="right")
ax.text(0.62, 44, "linear K$_d$ = 100 L/kg\n(no limit)", color=GREY, fontsize=14)
ax.text(1.0, 11, "Langmuir: sites fill up", color=GREEN, fontsize=14)
ax.set_xlim(0, 2.0)
ax.set_ylim(0, 60)
ax.set_xlabel("Water concentration C$_w$ (mg/L)")
ax.set_ylabel("Sorbed q (mg/kg)")
ax.set_title("Same start, different limit", fontsize=16, color=INK, loc="left")
save(fig, "isotherms.svg")

# ---------------------------------------------------------------- 7 filtered vs unfiltered at two sites (constructed)
fig, ax = plt.subplots(figsize=(7.4, 4.7))
sites = [("upstream", 8.0, 10.0), ("downstream", 2.0, 9.5)]       # constructed ug/L: filtered, total
for i, (lab, filt, tot) in enumerate(sites):
    ax.bar(i - 0.17, filt, width=0.32, color=BLUE)
    ax.bar(i + 0.17, tot, width=0.32, color=SOLID)
    ax.text(i - 0.17, filt + 0.25, f"{filt:.1f}", ha="center", fontsize=14, color=BLUE)
    ax.text(i + 0.17, tot + 0.25, f"{tot:.1f}", ha="center", fontsize=14, color=SOLID)
ax.set_xticks([0, 1], [s_[0] for s_ in sites])
ax.text(1.55, 7.5, "unfiltered\n(total)", color=SOLID, fontsize=14, fontweight="bold")
ax.text(1.55, 3.0, "filtered", color=BLUE, fontsize=14, fontweight="bold")
ax.set_xlim(-0.5, 2.1)
ax.set_ylim(0, 12)
ax.set_ylabel("Metal (µg/L)")
ax.set_title("Constructed river samples", fontsize=16, color=INK, loc="left")
save(fig, "filtered-total.svg")

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
