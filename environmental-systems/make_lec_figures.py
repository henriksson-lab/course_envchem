"""Model figures for the balances lecture (environmental-systems/lec.qmd).

All inputs are constructed teaching cases, not measured data. Values match
notes.qmd and exercise.qmd.
Run from the repository root:  python3 environmental-systems/make_lec_figures.py
Writes SVG files to environmental-systems/fig/ and prints the values quoted on slides.
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


# ---------------------------------------------------------------- numbers
print("mix:", (2.00 * 3.00 + 1.00 * 0.600) / 3.00, "mg/L")
print("load: g/s", 0.200 * 1000 * 0.500 / 1000, "kg/day", 0.200 * 1000 * 0.500 * 86400 / 1e6)
print("junction:", (40 * 0.50 + 10 * 2.00) / 50, "mg/L")
print("nitrate factor 62.00/14.007 =", 62.00 / 14.007)
V_VAT, Q_VAT = 77e9, 40.0
print("Vattern tau (yr):", V_VAT / Q_VAT / (365.25 * 86400))

# ---------------------------------------------------------------- 1 two-phase bottle
fig, ax = plt.subplots(figsize=(6.6, 4.8))
x = [0, 1]
ax.bar(0, 10.0, color=BLUE, width=0.7)
ax.bar(1, 4.0, color=BLUE, width=0.7)
ax.bar(1, 5.0, bottom=4.0, color="#7a5a2b", width=0.7)
ax.bar(1, 1.0, bottom=9.0, color="white", edgecolor=RUST, hatch="//", lw=2, width=0.7)
ax.text(0, 5.0, "water\n10.0 mg", ha="center", va="center", color="white", fontsize=16, fontweight="bold")
ax.text(1, 2.0, "water\n4.0 mg", ha="center", va="center", color="white", fontsize=15, fontweight="bold")
ax.text(1, 6.5, "sediment\n5.0 mg", ha="center", va="center", color="white", fontsize=15, fontweight="bold")
ax.annotate("unaccounted 1.0", (1.36, 9.5), xytext=(1.5, 9.5), va="center", color=RUST,
            fontsize=15, fontweight="bold", arrowprops=dict(arrowstyle="->", color=RUST))
ax.set_xticks(x, ["start", "later"])
ax.set_xlim(-0.5, 2.3)
ax.set_ylim(0, 11.2)
ax.set_ylabel("Parent compound (mg)")
ax.set_title("Sealed bottle: where is the parent?", fontsize=16, color=INK, loc="left")
save(fig, "two-phase-bottle.svg")

# ---------------------------------------------------------------- 2 approach to steady state
# Constructed lake: V = 1.0e6 m3, Q = 1.0e4 m3/day (tau = 100 d), load I = 1.0 kg/day,
# starting clean, conservative solute.
V, Q, I = 1.0e6, 1.0e4, 1.0
tau = V / Q
t = np.linspace(0, 500, 400)
M = I * tau * (1 - np.exp(-t / tau))           # kg
out = Q * (M / V)                               # kg/day
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3))
a1.plot(t, M, color=BLUE, lw=3)
a1.axhline(I * tau, color=GREY, ls=":", lw=1.5)
a1.text(495, I * tau * 1.04, "steady inventory 100 kg", ha="right", color=GREY, fontsize=14)
a1.set_xlabel("time (days)")
a1.set_ylabel("solute in lake, M (kg)")
a1.set_ylim(0, 115)
a1.set_title("Inventory levels off", fontsize=16, color=INK, loc="left")
a2.plot(t, np.full_like(t, I), color=GREEN, lw=3)
a2.plot(t, out, color=RUST, lw=3)
a2.text(20, 1.05, "input I = 1.0 kg/day", color=GREEN, fontsize=14)
a2.text(150, 0.45, "output QC", color=RUST, fontsize=14)
a2.text(495, 0.15, "steady state:\ninput = output,\nboth still running", ha="right",
        color=INK, fontsize=14)
a2.set_xlabel("time (days)")
a2.set_ylabel("flux (kg/day)")
a2.set_ylim(0, 1.25)
a2.set_title("Fluxes do not stop", fontsize=16, color=INK, loc="left")
fig.tight_layout(w_pad=3)
save(fig, "steady-state.svg")

# ---------------------------------------------------------------- 3 mixing line
fig, ax = plt.subplots(figsize=(6.6, 4.8))
f = np.linspace(0, 1, 50)
ax.plot(f, 0.600 + (3.00 - 0.600) * f, color=BLUE, lw=3)
ax.plot([0, 1], [0.600, 3.00], "o", color=INK, ms=9)
ax.text(0.03, 0.42, "water 2\n0.600 mg/L", fontsize=14, color=INK, va="top")
ax.text(0.97, 3.12, "water 1\n3.00 mg/L", fontsize=14, color=INK, ha="right", va="bottom")
ax.plot(2 / 3, 2.20, "o", ms=12, mfc="white", mec=BLUE, mew=3, zorder=4)
ax.annotate("2 L + 1 L mix\n2.20 mg/L", (2 / 3, 2.20), xytext=(0.18, 2.55), fontsize=14,
            color=BLUE, arrowprops=dict(arrowstyle="->", color=BLUE))
ax.plot(2 / 3, 1.50, "s", ms=11, color=RUST)
ax.annotate("a measured value here\nmeans something else\nhappened (loss, reaction,\nsampling error)",
            (2 / 3, 1.50), xytext=(0.62, 0.25), fontsize=13, color=RUST,
            arrowprops=dict(arrowstyle="->", color=RUST))
ax.set_xlabel("fraction of water 1 in the mixture")
ax.set_ylabel("concentration (mg/L)")
ax.set_ylim(0, 3.7)
ax.set_title("Conservative mixing line (constructed)", fontsize=16, color=INK, loc="left")
save(fig, "mixing-line.svg")

# ---------------------------------------------------------------- 4 flushing vs reaction
tt = np.linspace(0, 4, 300)
fig, ax = plt.subplots(figsize=(7.4, 4.8))
ax.plot(tt, np.exp(-tt), color=BLUE, lw=3)
ax.plot(tt, np.exp(-2 * tt), color=RUST, lw=3)
ax.plot(1, np.exp(-1), "o", color=BLUE, ms=9)
ax.annotate("t = τ: 0.37 left", (1, np.exp(-1)), xytext=(1.5, 0.62), fontsize=14, color=BLUE,
            arrowprops=dict(arrowstyle="->", color=BLUE))
ax.text(2.2, 0.20, "flushing only (conservative)", color=BLUE, fontsize=14)
ax.annotate("flushing + reaction\n(here k = 1/τ)", (0.75, np.exp(-1.5)), xytext=(1.7, 0.38), color=RUST, fontsize=14, arrowprops=dict(arrowstyle="->", color=RUST))
ax.set_xlabel("time / hydraulic replacement time  (t / τ)")
ax.set_ylabel("C / C$_0$")
ax.set_ylim(0, 1.05)
ax.set_title("Clean inflow, well-mixed lake (model)", fontsize=16, color=INK, loc="left")
save(fig, "flushing.svg")

# ---------------------------------------------------------------- 5 a pulse travelling downstream
# Constructed conservative tracer: 100 kg released at once. Each station sees a
# Gaussian pulse; flow grows downstream (tributaries) and the pulse spreads.
MASS_G = 100e3
stations = [("station 1", 50.0, 3.0, 10.0, BLUE, (16, 62)),
            ("station 2", 150.0, 6.0, 30.0, GREEN, (36, 34)),
            ("station 3", 600.0, 12.0, 70.0, RUST, (74, 22))]
th = np.linspace(0, 110, 1200)
fig, ax = plt.subplots(figsize=(10.5, 4.6))
for name, q, sig, t0, col, pos in stations:
    c = MASS_G / (q * sig * 3600 * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((th - t0) / sig) ** 2)  # g/m3
    c_ug = c * 1000  # ug/L
    ax.plot(th, c_ug, color=col, lw=3)
    ax.fill_between(th, c_ug, color=col, alpha=0.12)
    load = q * np.trapezoid(c, th * 3600) / 1000
    print(f"{name}: Q={q} peak {c_ug.max():.1f} ug/L, passing mass {load:.1f} kg")
    ax.text(pos[0], pos[1], f"{name}\nQ = {q:.0f} m³/s\npeak {c_ug.max():.0f} µg/L",
            color=col, fontsize=14, va="top")
ax.set_xlabel("time after release (hours)")
ax.set_ylabel("concentration (µg/L)")
ax.set_xlim(0, 110)
ax.set_title("Peak falls about 50-fold, yet 100 kg passes every station", fontsize=16,
             color=INK, loc="left")
save(fig, "plume.svg")
print("wrote figures to", OUT)
