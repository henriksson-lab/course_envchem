"""Model figures for the soil chemistry lecture (soil-chemistry/lec.qmd).

Constructed teaching illustrations, not measured data. Typical ranges are
rounded textbook values and vary with method and pH.
Run from the repository root:  python3 soil-chemistry/make_lec_figures.py
Writes SVG files to soil-chemistry/fig/ and prints the values quoted on slides.
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


# ---------------------------------------------------------------- numbers quoted on slides
cec, mass = 10.0, 0.200
charge = cec * 0.01 * mass
print(f"worked: {charge:.4f} mol charge; half as Ca: {charge/2:.4f} mol charge = {charge/4:.5f} mol Ca")
print(f"exercise 1: {20.0*0.01*0.100:.4f} mol charge -> {20.0*0.01*0.100/2:.4f} mol Mg")
print(f"exercise 2: base saturation {9.00/12.0*100:.1f} %")
print(f"exercise 3: {0.0100*2:.4f} mol H+ eq")
LOGK_GIBBSITE = 8.11  # Al(OH)3(s) + 3H+ = Al3+ + 3H2O, 25 C, crystalline gibbsite
for ph in (6.0, 5.5, 5.0, 4.5, 4.0):
    al = 10 ** (LOGK_GIBBSITE - 3 * ph)
    print(f"gibbsite free Al3+ at pH {ph}: {al:.2e} mol/L = {al*26.98e6:.3g} ug/L")
# Restoration example: 1 ha, 0.10 m layer, bulk density 1.0 kg/L -> 1.0e6 kg soil
soil_kg = 1e4 * 0.10 * 1000 * 1.0
add_cmolc = 1.0
mol_c = add_cmolc * 0.01 * soil_kg
print(f"restore: {soil_kg:.3g} kg soil, {mol_c:.0f} mol charge, {mol_c/2:.0f} mol Ca = "
      f"{mol_c/2*40.08/1000:.0f} kg Ca = {mol_c/2*100.09/1000:.0f} kg CaCO3")

# ---------------------------------------------------------------- 1 CEC ranges
ranges = [
    ("Quartz sand", 1, 5, "#c9b27c"),
    ("Kaolinite clay", 3, 15, RUST),
    ("Illite clay", 10, 40, RUST),
    ("Smectite clay", 80, 120, RUST),
    ("Vermiculite", 100, 150, RUST),
    ("Soil organic matter", 150, 300, "#5b4636"),
]
fig, ax = plt.subplots(figsize=(7.0, 4.4))
for i, (name, lo, hi, col) in enumerate(ranges[::-1]):
    ax.plot([lo, hi], [i, i], color=col, lw=14, solid_capstyle="round")
    ax.text(hi * 1.25, i, f"{lo}–{hi}", va="center", fontsize=14, color=INK)
ax.set_yticks(range(len(ranges)), [r[0] for r in ranges[::-1]])
ax.set_xscale("log")
ax.set_xlim(0.7, 900)
ax.set_xticks([1, 10, 100, 1000], ["1", "10", "100", "1000"])
ax.set_xlabel("Cation exchange capacity (cmol$_c$/kg)")
ax.set_title("Approximate typical ranges; vary with pH and method", fontsize=14, color=GREY, loc="left")
ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False)
save(fig, "cec-ranges.svg")

# ---------------------------------------------------------------- 2 exchanger occupancy, two soils
ions = ["Ca$^{2+}$", "Mg$^{2+}$", "K$^+$", "Na$^+$", "Al$^{3+}$ + H$^+$"]
icol = ["#2468A0", "#5b8fbd", "#8fb3d4", "#c3d6e8", RED]
soilA = [1.2, 0.3, 0.12, 0.08, 1.3]
soilB = [11.0, 2.5, 0.5, 0.2, 5.8]
for nm, s in (("A", soilA), ("B", soilB)):
    print(f"soil {nm}: CEC {sum(s):.1f}, base cations {sum(s[:4]):.1f}, BS {100*sum(s[:4])/sum(s):.0f}%")
fig, ax = plt.subplots(figsize=(5.4, 4.6))
for xi, s in enumerate((soilA, soilB)):
    bottom = 0
    for v, col, nm in zip(s, icol, ions):
        ax.bar(xi, v, bottom=bottom, color=col, width=0.55, edgecolor="white", lw=1)
        if v > 2.0:
            ax.text(xi, bottom + v / 2, nm, ha="center", va="center", fontsize=13,
                    color="white" if col in (RED, "#2468A0") else INK)
        bottom += v
    ax.text(xi, bottom + 0.4, f"CEC {bottom:.0f}\nBS {100*sum(s[:4])/bottom:.0f}%", ha="center",
            fontsize=13, color=INK)
ax.set_xticks([0, 1], ["Soil A\nsandy podzol", "Soil B\nclay loam"])
for j, (nm, col) in enumerate(zip(ions[::-1], icol[::-1])):
    ax.add_patch(plt.Rectangle((1.45, 16 - 2.2 * j), 0.12, 1.4, color=col, clip_on=False))
    ax.text(1.62, 16.7 - 2.2 * j, nm, va="center", fontsize=13, color=INK)
ax.set_xlim(-0.45, 1.4)
ax.set_ylabel("Exchange charge (cmol$_c$/kg)")
ax.set_ylim(0, 25)
ax.set_title("Both soils: pH about 5 (constructed)", fontsize=14, color=GREY, loc="left")
save(fig, "occupancy.svg")

# ---------------------------------------------------------------- 3 buffer ranges (after Ulrich)
buf = [
    ("Carbonate", 6.2, 8.6, "CaCO$_3$ + 2H$^+$ → Ca$^{2+}$ + CO$_2$ + H$_2$O", BLUE),
    ("Silicate weathering", 5.0, 6.2, "slow release of base cations from minerals", GREEN),
    ("Cation exchange", 4.2, 5.0, "H$^+$/Al$^{3+}$ displace Ca$^{2+}$, Mg$^{2+}$ from sites", ACCENT),
    ("Aluminium", 3.0, 4.2, "Al(OH)$_3$ + 3H$^+$ → Al$^{3+}$ + 3H$_2$O", RED),
    ("Iron", 2.4, 3.8, "Fe(III) oxides dissolve", "#7a3b1e"),
]
fig, ax = plt.subplots(figsize=(9.0, 4.4))
for i, (name, lo, hi, txt, col) in enumerate(buf):
    y = len(buf) - 1 - i
    ax.barh(y, hi - lo, left=lo, height=0.62, color=col, alpha=0.9)
    ax.text((lo + hi) / 2, y, f"{lo}–{hi}", ha="center", va="center", fontsize=13, color="white")
ax.set_yticks(range(len(buf)), [b[0] for b in buf[::-1]])
ax.tick_params(axis="y", length=0)
ax.set_xlim(2, 9)
ax.set_xticks(range(2, 10))
ax.invert_xaxis()
ax.spines["left"].set_visible(False)
ax.set_xlabel("Approximate soil pH range (acid input pushes the soil to the right →)")
save(fig, "buffer-ranges.svg")

# ---------------------------------------------------------------- 4 aluminium solubility
ph = np.linspace(3.8, 6.4, 200)
al = 10 ** (LOGK_GIBBSITE - 3 * ph) * 26.98e6  # ug/L
fig, ax = plt.subplots(figsize=(5.8, 4.6))
ax.plot(ph, al, color=RED, lw=3)
for p in (5.5, 5.0, 4.5):
    v = 10 ** (LOGK_GIBBSITE - 3 * p) * 26.98e6
    ax.plot(p, v, "o", color=INK, ms=8, zorder=3)
    lab = f"{v:.0f}" if v >= 1 else f"{v:.2f}"
    ax.annotate(f"pH {p}: ≈ {lab} µg/L", (p, v), xytext=(14, -6), textcoords="offset points",
                fontsize=13, color=INK, va="top")
ax.set_yscale("log")
ax.set_xlim(3.8, 6.4)
ax.set_ylim(0.003, 3e4)
ax.invert_xaxis()
ax.set_xlabel("pH (more acidic →)")
ax.set_ylabel("Free Al$^{3+}$ at gibbsite\nsaturation (µg/L)")
ax.set_title("One pH unit lower: 1000 × more Al$^{3+}$", fontsize=15, color=INK, loc="left")
save(fig, "al-solubility.svg")

# ---------------------------------------------------------------- 5 inventories consumed by acid
# Soil A: no carbonate, exchangeable base cations 1.7 cmolc/kg.
# Soil B: no carbonate, exchangeable base cations 14.2 cmolc/kg (both as in occupancy.svg).
q = np.linspace(0, 30, 600)
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), sharey=True)
for ax, (name, carb, exch) in zip(axes, (("Soil A (sandy, no carbonate)", 0.0, 1.7),
                                          ("Soil B (clay loam, no carbonate)", 0.0, 14.2))):
    carb_left = np.clip(carb - q, 0, None)
    exch_left = np.clip(exch - np.clip(q - carb, 0, None), 0, None)
    ax.stackplot(q, carb_left, exch_left, colors=[BLUE, ACCENT], alpha=0.9)
    end = carb + exch
    ax.axvline(end, color=RED, ls="--", lw=1.8)
    ax.text(end + 0.5, 15, f"{end:.1f}: bases\nexhausted →\nAl buffering", color=RED, fontsize=12, va="top")
    ax.set_title(name, fontsize=14, color=INK, loc="left")
    ax.set_xlabel("Cumulative acid added (cmol$_c$/kg)")
    ax.set_xlim(0, 18)
axes[0].set_ylabel("Remaining inventory\n(cmol$_c$/kg)")
axes[0].set_ylim(0, 16)
axes[1].text(1.0, 3.0, "exchangeable\nbase cations", color=INK, fontsize=12)
axes[0].annotate("exchangeable\nbase cations", (0.5, 1.0), xytext=(4, 8), fontsize=12, color=INK,
                 arrowprops=dict(arrowstyle="->", color=INK))
fig.text(0.5, -0.05, "Constructed illustration (soils of the previous slide); slow weathering, uptake and rates ignored.",
         ha="center", fontsize=12, color=GREY)
fig.tight_layout()
save(fig, "inventory-depletion.svg")

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
