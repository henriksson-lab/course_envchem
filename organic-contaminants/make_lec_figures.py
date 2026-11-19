"""Model figures for the organic contaminants lecture (organic-contaminants/lec.qmd).

Fictitious compounds U and V use the inputs of compounds.csv (activity C).
log Kow values are rounded literature values, shown for orientation only.
Run from the repository root:  python3 organic-contaminants/make_lec_figures.py
Writes SVG files to organic-contaminants/fig/ and prints the values quoted on slides.
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
C_U, C_V = "#2468A0", "#AD4825"

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


VW, MS, M0 = 1.00, 0.0100, 1.00
CASES = {"U": dict(kd=100.0, t_half=10.0, col=C_U), "V": dict(kd=10.0, t_half=30.0, col=C_V)}


def total(t, t_half):
    return M0 * np.exp(-np.log(2) / t_half * t)


def water_conc(t, kd, t_half):
    return total(t, t_half) / (VW + kd * MS)


def f_neutral(pH, pka):
    return 1 / (1 + 10 ** (pH - pka))


# ---------------------------------------------------------------- numbers quoted on slides
print(f"Kd = 0.0200*5000 = {0.0200*5000:.0f} L/kg; wrong percent: {2.00*5000:.0f}")
print(f"neutral fraction pKa 4.5: pH 4.5 {f_neutral(4.5, 4.5):.3f}, pH 6.5 {f_neutral(6.5, 4.5):.6f}, "
      f"pH 7.0 {f_neutral(7.0, 4.5):.5f}")
for name, c in CASES.items():
    fw = VW / (VW + c["kd"] * MS)
    print(f"{name}: water fraction {fw:.4f}; Cw0 {water_conc(0, c['kd'], c['t_half']):.4f}; "
          f"day20 total {total(20, c['t_half']):.4f} Cw {water_conc(20, c['kd'], c['t_half']):.4f}; "
          f"day30 total {total(30, c['t_half']):.4f} Cw {water_conc(30, c['kd'], c['t_half']):.4f}")

# ---------------------------------------------------------------- 1 log Kow scale
kow = [("ethanol", -0.31), ("benzene", 2.13), ("atrazine", 2.61), ("naphthalene", 3.30),
       ("lindane", 3.72), ("p,p′-DDT", 6.91)]
labpos = {"ethanol": (-0.31, 0.5), "benzene": (1.85, -0.5), "atrazine": (2.61, 0.5),
          "naphthalene": (3.55, -0.5), "lindane": (3.95, 0.5), "p,p′-DDT": (6.91, 0.5)}
fig, ax = plt.subplots(figsize=(10.0, 3.8))
ax.axhline(0, color=INK, lw=2)
for name, v in kow:
    ax.plot(v, 0, "o", ms=14, color=BLUE if v < 4 else RUST, zorder=3)
    ax.annotate(name, (v, 0), xytext=labpos[name], ha="center", va="center", fontsize=15, color=INK,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=1))
ax.set_xlim(-1.2, 8.0)
ax.set_ylim(-0.9, 0.9)
ax.set_yticks([])
ax.spines["left"].set_visible(False)
ax.set_xticks(range(-1, 9))
ax.set_xlabel("log K$_{ow}$   (← stays in water          seeks organic matter and fat →)")
ax.set_title("Approximate literature values", fontsize=14, color=GREY, loc="left")
save(fig, "logkow-scale.svg")

# ---------------------------------------------------------------- 2 neutral fraction vs pH
ph = np.linspace(2, 9, 400)
fig, ax = plt.subplots(figsize=(5.8, 4.4))
ax.plot(ph, f_neutral(ph, 4.5), color=BLUE, lw=3, label="neutral HA")
ax.plot(ph, 1 - f_neutral(ph, 4.5), color=RUST, lw=3, label="anion A$^-$")
for p in (4.5, 6.5):
    v = f_neutral(p, 4.5)
    ax.plot(p, v, "o", color=INK, ms=8, zorder=3)
lab = {4.5: "pH 4.5: 0.500", 6.5: "pH 6.5: 0.0099"}
ax.annotate(lab[4.5], (4.5, 0.5), xytext=(5.1, 0.62), fontsize=14, color=INK,
            arrowprops=dict(arrowstyle="->", color=INK))
ax.annotate(lab[6.5], (6.5, f_neutral(6.5, 4.5)), xytext=(6.7, 0.25), fontsize=14, color=INK,
            arrowprops=dict(arrowstyle="->", color=INK))
ax.axvspan(6.0, 8.5, color=GREEN, alpha=0.08, lw=0)
ax.text(7.25, 1.04, "most natural waters", ha="center", fontsize=12, color=GREEN)
ax.set_xlabel("pH")
ax.set_ylabel("Fraction of total")
ax.set_ylim(0, 1.08)
ax.set_title("Fictitious organic acid, pK$_a$ = 4.50", fontsize=14, color=GREY, loc="left")
ax.text(2.1, 0.88, "neutral HA", color=BLUE, fontsize=14, fontweight="bold")
ax.text(2.1, 0.07, "anion A$^-$", color=RUST, fontsize=14, fontweight="bold")
save(fig, "ionisation.svg")

# ---------------------------------------------------------------- 3 phase split vs Kd
kd = np.logspace(-1, 4, 300)
fw = VW / (VW + kd * MS)
fig, ax = plt.subplots(figsize=(6.0, 4.4))
ax.fill_between(kd, 0, fw, color=BLUE, alpha=0.75, lw=0)
ax.fill_between(kd, fw, 1, color="#c9a66b", alpha=0.85, lw=0)
ax.text(0.3, 0.45, "in water", color="white", fontsize=16, fontweight="bold")
ax.text(2500, 0.88, "on solid", color=INK, fontsize=16, fontweight="bold", ha="center")
for name, c in CASES.items():
    f = VW / (VW + c["kd"] * MS)
    ax.plot(c["kd"], f, "o", ms=10, color="white", mec=INK, mew=2, zorder=3)
    ax.annotate(f"{name}: K$_d$ = {c['kd']:.0f}\n{f:.3f} in water", (c["kd"], f),
                xytext=((c["kd"] * 0.9, f - 0.32) if name == "V" else (250, 0.6)), fontsize=13, color=INK,
                ha="right" if name == "V" else "left",
                arrowprops=dict(arrowstyle="->", color=INK))
ax.axvline(100, color=GREY, ls=":", lw=1.2)
ax.set_xscale("log")
ax.set_xlim(0.1, 1e4)
ax.set_ylim(0, 1)
ax.set_xlabel("K$_d$ (L/kg)")
ax.set_ylabel("Fraction of parent")
ax.set_title("1.00 L water + 0.0100 kg solid", fontsize=14, color=GREY, loc="left")
save(fig, "phase-split.svg")

# ---------------------------------------------------------------- 4 first-order loss of total parent
t = np.linspace(0, 60, 400)
fig, ax = plt.subplots(figsize=(6.0, 4.4))
for name, c in CASES.items():
    ax.plot(t, total(t, c["t_half"]), color=c["col"], lw=3, label=f"{name}: t$_{{1/2}}$ = {c['t_half']:.0f} d")
for k in (1, 2, 3):
    ax.plot(10 * k, 0.5 ** k, "o", color=C_U, ms=8)
    ax.annotate(f"{0.5**k:g}", (10 * k, 0.5 ** k), xytext=(6, 6), textcoords="offset points", fontsize=13, color=C_U)
ax.set_xlabel("Time (days)")
ax.set_ylabel("Total parent (mg)")
ax.set_ylim(0, 1.05)
ax.set_xlim(0, 60)
ax.legend(frameon=False, fontsize=14)
ax.set_title("Each half-life halves what is left", fontsize=15, color=INK, loc="left")
save(fig, "first-order.svg")

# ---------------------------------------------------------------- 5 water concentration, U and V
fig, ax = plt.subplots(figsize=(8.0, 4.6))
for name, c in CASES.items():
    ax.plot(t, water_conc(t, c["kd"], c["t_half"]), color=c["col"], lw=3, label=name)
pts = [("U", 0), ("V", 0), ("U", 20), ("U", 30), ("V", 30)]
for name, d in pts:
    c = CASES[name]
    v = water_conc(d, c["kd"], c["t_half"])
    ax.plot(d, v, "o", color=c["col"], ms=8, zorder=3)
    ax.annotate(f"{v:.4g}", (d, v), xytext=(7, 5), textcoords="offset points", fontsize=13, color=c["col"])
ax.set_xlabel("Time (days)")
ax.set_ylabel("Water parent (mg/L)")
ax.set_xlim(0, 60)
ax.set_ylim(0, 1.0)
ax.legend(frameon=False, fontsize=14, title="compound", title_fontsize=13)
ax.set_title("Model prediction, not data", fontsize=14, color=GREY, loc="left")
save(fig, "fate-water.svg")

# ---------------------------------------------------------------- 6 inventory of U
c = CASES["U"]
tot = total(t, c["t_half"])
fw = VW / (VW + c["kd"] * MS)
fig, ax = plt.subplots(figsize=(6.6, 4.6))
ax.stackplot(t, tot * fw, tot * (1 - fw), M0 - tot, colors=[BLUE, "#c9a66b", "#d0d6dd"])
ax.text(1.0, 0.2, "in water", color="white", fontsize=14, fontweight="bold")
ax.text(1.0, 0.62, "on solid", color=INK, fontsize=14, fontweight="bold")
ax.text(31, 0.48, "transformed parent\n(products: identity and\ntoxicity not tracked)", color=INK, fontsize=13)
ax.axvline(20, color=INK, lw=1.5, ls="--")
ax.text(21.5, 0.90, "day 20:\n0.125 + 0.125 + 0.750\n= 1.00 mg", fontsize=13, color=INK, va="top")
ax.set_xlim(0, 60)
ax.set_ylim(0, 1.0)
ax.set_xlabel("Time (days)")
ax.set_ylabel("Mass (mg)")
ax.set_title("Compound U: every milligram accounted for", fontsize=15, color=INK, loc="left")
save(fig, "inventory-u.svg")

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
