"""Model figures for the atmospheric reactions lecture (atmospheric-reactions/lec.qmd).

Temperature uses the US Standard Atmosphere (1976) lapse rates. The ozone
profile is a schematic shape, not a measurement. Rate numbers are the
constructed teaching case from exercise.qmd.
Run from the repository root:  python3 atmospheric-reactions/make_lec_figures.py
Writes SVG files to atmospheric-reactions/fig/ and prints the values quoted on slides.
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
PURPLE = "#6a4c93"

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
HC_NA = 6.62607e-34 * 2.99792e8 * 6.02214e23 * 1e9 / 1000  # kJ nm / mol
print(f"E = {HC_NA:.0f} kJ nm/mol / lambda")
for name, bond in (("O2", 498.0), ("NO-O in NO2", 306.0)):
    print(f"{name}: {bond} kJ/mol -> {HC_NA / bond:.0f} nm")
K, OH = 1.0e-12, 1.0e6
kp = K * OH
tau_s = 1 / kp
print(f"k' = {kp:.1e} 1/s, tau = {tau_s:.2e} s = {tau_s / 86400:.2f} d, t1/2 = {np.log(2) * tau_s / 86400:.2f} d")


# ---------------------------------------------------------------- 1 temperature + ozone profile
def std_temp(z):
    layers = [(0, 288.15, -6.5), (11, 216.65, 0.0), (20, 216.65, 1.0), (32, 228.65, 2.8),
              (47, 270.65, 0.0), (51, 270.65, -2.8)]
    t = np.zeros_like(z)
    for i, (z0, t0, lapse) in enumerate(layers):
        z1 = layers[i + 1][0] if i + 1 < len(layers) else 1e9
        m = (z >= z0) & (z < z1)
        t[m] = t0 + lapse * (z[m] - z0)
    return t - 273.15


z = np.linspace(0, 60, 601)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 5.2), sharey=True)
a1.plot(std_temp(z), z, color=RUST, lw=3)
for a in (a1, a2):
    a.axhspan(0, 11, color="#d6e6f2", alpha=0.6, lw=0)
    a.axhspan(11, 50, color="#eef4fa", alpha=0.8, lw=0)
a1.text(-85, 5, "troposphere", fontsize=14, color=INK)
a1.text(-85, 40, "stratosphere", fontsize=14, color=INK)
a1.text(-85, 54, "mesosphere", fontsize=14, color=INK)
a1.set_xlabel("temperature (°C)")
a1.set_ylabel("altitude (km)")
a1.set_xlim(-90, 25)
a1.set_title("Standard atmosphere", fontsize=16, color=INK, loc="left")
oz = np.exp(-0.5 * ((z - 22) / 6.5) ** 2) + 0.03 * np.exp(-z / 3)
a2.plot(oz, z, color=PURPLE, lw=3)
a2.fill_betweenx(z, oz, color=PURPLE, alpha=0.15)
a2.annotate("ozone layer:\nabsorbs UV\n(protective)", (0.95, 22), xytext=(0.45, 34), fontsize=14,
            color=PURPLE, arrowprops=dict(arrowstyle="->", color=PURPLE))
a2.annotate("ground-level ozone:\nbreathed in\n(harmful)", (0.04, 1), xytext=(0.30, 4.5),
            fontsize=14, color=RUST, arrowprops=dict(arrowstyle="->", color=RUST))
a2.set_xlabel("ozone concentration (relative)")
a2.set_xticks([])
a2.set_title("Ozone (schematic shape)", fontsize=16, color=INK, loc="left")
a2.set_ylim(0, 60)
fig.tight_layout(w_pad=2)
save(fig, "atmosphere-profile.svg")

# ---------------------------------------------------------------- 2 photon energy
lam = np.linspace(150, 800, 500)
fig, ax = plt.subplots(figsize=(7.6, 5.4))
bands = [(150, 280, "UV-C", "#e8dff5"), (280, 315, "UV-B", "#f3e3d3"), (315, 400, "UV-A", "#fbefd5"),
         (400, 700, "visible", "#eef4fa")]
for lo, hi, lab, col in bands:
    ax.axvspan(lo, hi, color=col, lw=0)
    ax.text((lo + hi) / 2, 770, lab, ha="center", fontsize=13 if hi - lo < 60 else 14, color=INK, rotation=90 if hi - lo < 60 else 0, va="top")
ax.plot(lam, HC_NA / lam, color=INK, lw=3)
for bond, lab, col, dx in ((498, "O$_2$: 498 kJ/mol", BLUE, 12),
                           (306, "NO$_2$: 306 kJ/mol", GREEN, 12)):
    lcut = HC_NA / bond
    ax.axhline(bond, color=col, ls="--", lw=2)
    ax.plot(lcut, bond, "o", color=col, ms=10, zorder=4)
    ax.text(lcut + dx, bond + 18, f"{lab}\nneeds λ < {lcut:.0f} nm", color=col, fontsize=15)
ax.set_xlim(150, 800)
ax.set_ylim(0, 820)
ax.set_xlabel("wavelength λ (nm)")
ax.set_ylabel("photon energy (kJ/mol)")
ax.set_title("Shorter wavelength, more energy", fontsize=16, color=INK, loc="left")
save(fig, "photon-energy.svg")

# ---------------------------------------------------------------- 3 lifetime decay
days = np.linspace(0, 40, 400)
tau_d = tau_s / 86400
fig, ax = plt.subplots(figsize=(7.2, 4.8))
ax.plot(days, np.exp(-days / tau_d), color=BLUE, lw=3)
ax.plot(tau_d, np.exp(-1), "o", color=BLUE, ms=9)
ax.plot(np.log(2) * tau_d, 0.5, "o", color=RUST, ms=9)
ax.annotate(f"lifetime τ = {tau_d:.1f} d\n0.37 left", (tau_d, np.exp(-1)), xytext=(17, 0.55),
            fontsize=14, color=BLUE, arrowprops=dict(arrowstyle="->", color=BLUE))
ax.annotate(f"half-life = {np.log(2) * tau_d:.1f} d\n0.50 left", (np.log(2) * tau_d, 0.5),
            xytext=(10, 0.78), fontsize=14, color=RUST, arrowprops=dict(arrowstyle="->", color=RUST))
ax.set_xlabel("time (days)")
ax.set_ylabel("fraction remaining")
ax.set_ylim(0, 1.05)
ax.set_title("One sink: X + OH, with OH held constant", fontsize=16, color=INK, loc="left")
save(fig, "lifetime-decay.svg")

# ---------------------------------------------------------------- 4 lifetimes vs mixing times
SEC = {"s": 1, "h": 3600, "d": 86400, "yr": 3.156e7}
fig, ax = plt.subplots(figsize=(11, 4.4))
ax.set_xscale("log")
ax.set_xlim(0.3, 3e10)
ax.set_ylim(0, 3)
ax.spines["left"].set_visible(False)
ax.set_yticks([])
mix = [(1 * SEC["d"], 3 * SEC["d"], "mixing up through\nthe lowest air layer", "right", 0.6),
       (3 * SEC["d"] * 7, 8 * SEC["d"] * 7, "around the globe\nwithin a hemisphere", "center", 1.0),
       (1 * SEC["yr"], 2 * SEC["yr"], "between\nhemispheres", "left", 0.6)]
for lo, hi, lab, ha, y in mix:
    ax.axvspan(lo, hi, ymin=0, ymax=0.3, color="#d6e6f2", lw=0)
    x = {"right": lo / 1.4, "center": np.sqrt(lo * hi), "left": hi * 1.4}[ha]
    ax.text(x, y - 0.35 if ha != "center" else y, lab, ha=ha, fontsize=13, color=BLUE)
ax.text(0.5, 1.25, "transport times (approximate):", fontsize=14, color=BLUE)
gases = [(1, "OH radical\n≈ 1 s", RUST, "center"), (tau_s, "exercise gas\n11.6 days", INK, "center"),
         (10 * SEC["yr"], "methane\n≈ a decade", GREEN, "right"),
         (100 * SEC["yr"], "CFC-12\n≈ a century", PURPLE, "left")]
for t, lab, col, ha in gases:
    ax.plot(t, 2.0, "v", color=col, ms=14)
    x = {"center": t, "right": t / 1.3, "left": t * 1.3}[ha]
    ax.text(x, 2.25, lab, ha=ha, fontsize=14, color=col)
ax.text(0.5, 1.65, "chemical lifetimes:", fontsize=14, color=INK)
ticks = [1, 60, 3600, 86400, 3.156e7, 3.156e8, 3.156e9]
ax.set_xticks(ticks, ["1 s", "1 min", "1 h", "1 day", "1 yr", "10 yr", "100 yr"])
ax.minorticks_off()
ax.set_title("Short-lived gases stay near their sources; long-lived gases spread worldwide",
             fontsize=16, color=INK, loc="left")
save(fig, "lifetime-scale.svg")
print("wrote figures to", OUT)
