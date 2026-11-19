"""Model figures for the climate lecture (climate-chemistry/lec.qmd).

Blackbody curves use Planck's law; band positions are schematic; the CO2 response
uses the Joos et al. (2013) impulse-response fit used in IPCC AR5. Other inputs
are constructed teaching cases. Values match
notes.qmd and exercise.qmd.
Run from the repository root:  python3 climate-chemistry/make_lec_figures.py
Writes SVG files to climate-chemistry/fig/ and prints the values quoted on slides.
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
PURPLE = "#6a4c93"
H, C, KB = 6.62607e-34, 2.99792e8, 1.380649e-23


def planck_per_ln(lam_um, T):
    lam = lam_um * 1e-6
    b = 2 * H * C ** 2 / lam ** 5 / np.expm1(H * C / (lam * KB * T))
    return lam * b


# ---------------------------------------------------------------- numbers
k = 0.0200
print(f"lifetime {1 / k:.1f} d, half-life {np.log(2) / k:.1f} d, left after 50 d {np.exp(-k * 50):.3f}")
print("peak wavelengths (Wien, um):", 2898 / 5778, 2898 / 288)
A = [0.2173, 0.2240, 0.2824, 0.2763]
TAU = [394.4, 36.54, 4.304]


def co2_irf(t):
    return A[0] + sum(a * np.exp(-t / tt) for a, tt in zip(A[1:], TAU))


for t in (20, 100, 500):
    print(f"CO2 pulse left after {t} yr: {co2_irf(t):.2f}; 12-yr gas: {np.exp(-t / 12):.3f}")
print("molecules per kg ratio CH4/CO2:", 44.01 / 16.04)

# ---------------------------------------------------------------- 1 planck
lam = np.logspace(-1, 2, 600)
sun = planck_per_ln(lam, 5778) / lam      # spectral radiance per wavelength
earth = planck_per_ln(lam, 288) / lam
fig, ax = plt.subplots(figsize=(10, 4.6))
ax.fill_between(lam, sun / sun.max(), color=ACCENT, alpha=0.35, lw=0)
ax.plot(lam, sun / sun.max(), color=ACCENT, lw=3)
ax.fill_between(lam, earth / earth.max(), color=RUST, alpha=0.25, lw=0)
ax.plot(lam, earth / earth.max(), color=RUST, lw=3)
ax.text(0.55, 1.05, "sunlight (about 5800 K)\npeak near 0.5 µm", ha="center", fontsize=15, color="#8a6508")
ax.text(10, 1.05, "Earth's surface (about 288 K)\npeak near 10 µm", ha="center", fontsize=15, color=RUST)
ax.set_xscale("log")
ax.set_xlim(0.1, 100)
ax.set_ylim(0, 1.3)
ax.set_xticks([0.1, 0.3, 1, 3, 10, 30, 100], ["0.1", "0.3", "1", "3", "10", "30", "100"])
ax.set_yticks([])
ax.set_xlabel("wavelength (µm)")
ax.set_ylabel("emission (each scaled to its peak)")
ax.set_title("Shortwave in, longwave out: hardly overlapping", fontsize=16, color=INK, loc="left")
save(fig, "planck.svg")

# ---------------------------------------------------------------- 2 absorption bands (schematic)
lam = np.logspace(np.log10(3), np.log10(50), 500)
earth = planck_per_ln(lam, 288) / lam
fig, ax = plt.subplots(figsize=(10.5, 5.0))
ax.fill_between(lam, earth / earth.max(), color=RUST, alpha=0.15, lw=0)
ax.plot(lam, earth / earth.max(), color=RUST, lw=2.5)
ax.text(5.0, 0.8, "Earth's\nemission", color=RUST, fontsize=14, ha="center")
rows = [("H$_2$O", [(5.0, 8.0), (18, 50)], BLUE, 1.55),
        ("CO$_2$", [(4.1, 4.5), (13, 17)], INK, 1.40),
        ("O$_3$", [(9.3, 10.0)], PURPLE, 1.25),
        ("CH$_4$", [(7.4, 8.0)], GREEN, 1.10)]
for name, bands, col, y in rows:
    for lo, hi in bands:
        ax.plot([lo, hi], [y, y], color=col, lw=11, solid_capstyle="butt")
    ax.text(3.05, y, name, color=col, fontsize=15, va="center", fontweight="bold")
ax.axvspan(8, 13, ymax=0.62, color="#d6e6f2", alpha=0.7, lw=0)
ax.text(10.2, 0.35, "atmospheric\nwindow\n8–13 µm", ha="center", fontsize=14, color=BLUE)
ax.annotate("CO$_2$ bend, 15 µm:\nnear Earth's peak", (15, 1.40), xytext=(24, 1.22), fontsize=14,
            color=INK, arrowprops=dict(arrowstyle="->", color=INK))
ax.set_xscale("log")
ax.set_xlim(3, 50)
ax.set_ylim(0, 1.7)
ax.set_xticks([3, 5, 8, 10, 13, 15, 20, 30, 50], ["3", "5", "8", "10", "13", "15", "20", "30", "50"])
ax.minorticks_off()
ax.set_yticks([])
ax.set_xlabel("wavelength (µm)")
ax.set_title("Where gases absorb Earth's heat (schematic band positions)", fontsize=16, color=INK, loc="left")
save(fig, "absorption-bands.svg")

# ---------------------------------------------------------------- 3 teaching spectrum
lam = np.logspace(np.log10(0.3), np.log10(30), 500)
T = 0.95 - 0.75 * np.exp(-((np.log10(lam) - 1.0) / 0.12) ** 2)
fig, ax = plt.subplots(figsize=(7.4, 4.8))
ax.plot(lam, T, color=BLUE, lw=3)
for lx, tx, col in ((0.55, 0.95, ACCENT), (10, 0.20, RUST)):
    ax.plot(lx, tx, "o", color=col, ms=11, zorder=4)
ax.annotate("0.55 µm: T = 0.95\nabsorbed 0.05", (0.55, 0.95), xytext=(0.45, 0.55), fontsize=14,
            color="#8a6508", arrowprops=dict(arrowstyle="->", color="#8a6508"))
ax.annotate("10 µm: T = 0.20\nabsorbed 0.80", (10, 0.20), xytext=(1.6, 0.18), fontsize=14,
            color=RUST, arrowprops=dict(arrowstyle="->", color=RUST))
ax.set_xscale("log")
ax.set_xticks([0.3, 1, 3, 10, 30], ["0.3", "1", "3", "10", "30"])
ax.set_ylim(0, 1.08)
ax.set_xlabel("wavelength (µm)")
ax.set_ylabel("transmission T")
ax.set_title("Invented teaching spectrum (not a real gas)", fontsize=16, color=INK, loc="left")
save(fig, "teaching-spectrum.svg")

# ---------------------------------------------------------------- 4 first-order decay
d = np.linspace(0, 200, 400)
fig, ax = plt.subplots(figsize=(7.4, 4.8))
ax.plot(d, np.exp(-k * d), color=BLUE, lw=3)
ax.plot(np.log(2) / k, 0.5, "o", color=RUST, ms=10)
ax.plot(1 / k, np.exp(-1), "o", color=BLUE, ms=10)
ax.annotate("half-life 34.7 d: 0.50 left", (np.log(2) / k, 0.5), xytext=(60, 0.72), fontsize=14,
            color=RUST, arrowprops=dict(arrowstyle="->", color=RUST))
ax.annotate("lifetime 50.0 d: 0.368 left", (1 / k, np.exp(-1)), xytext=(80, 0.45), fontsize=14,
            color=BLUE, arrowprops=dict(arrowstyle="->", color=BLUE))
ax.set_xlabel("time (days)")
ax.set_ylabel("fraction remaining")
ax.set_ylim(0, 1.05)
ax.set_title("Fictitious gas, k = 0.0200 per day", fontsize=16, color=INK, loc="left")
save(fig, "decay-50d.svg")

# ---------------------------------------------------------------- 5 CO2 impulse response vs a 12-yr gas
t = np.linspace(0, 500, 1000)
fig, ax = plt.subplots(figsize=(10, 4.8))
ax.plot(t, co2_irf(t), color=INK, lw=3.2)
ax.plot(t, np.exp(-t / 12), color=GREEN, lw=3, ls="--")
ax.axhline(A[0], color=GREY, ls=":", lw=1.5)
ax.text(495, A[0] - 0.06, "about 20% still there after centuries", ha="right", fontsize=14, color=GREY)
ax.text(120, 0.55, "CO$_2$ pulse: several sinks, several timescales\n(ocean surface, land, deep ocean; fit used by IPCC)",
        fontsize=14, color=INK)
ax.text(60, 0.04, "single sink, lifetime about 12 years\n(similar to methane)", fontsize=14, color=GREEN)
ax.set_xlabel("years after a pulse is emitted")
ax.set_ylabel("fraction of pulse in the air")
ax.set_ylim(0, 1.05)
ax.set_xlim(0, 500)
ax.set_title("CO$_2$ has no single lifetime", fontsize=16, color=INK, loc="left")
save(fig, "co2-impulse.svg")
print("wrote figures to", OUT)
