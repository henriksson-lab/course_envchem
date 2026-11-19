"""Model figures for the gas-exchange and minerals lecture (carbonate-gases/gases-lec.qmd).

Constructed teaching-model predictions, not measured data: 25 degrees C, dilute
freshwater, constants from reference.qmd (pK1 6.35, pK2 10.33, KH 0.034, Ksp 3.3e-9).
Temperature effects are not modelled. Style copied from make_lec_figures.py.
Run from the repository root:  python3 carbonate-gases/make_gases_figures.py
Writes SVG files to carbonate-gases/fig/ (gases-*.svg) and prints quoted values.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PK1, PK2, KW, KH, KSP = 6.35, 10.33, 1.0e-14, 0.034, 3.3e-9
OUT = Path(__file__).resolve().parent / "fig"
OUT.mkdir(exist_ok=True)

C_CO2, C_HCO3, C_CO3 = "#2468A0", "#25713E", "#AD4825"
INK, GREY, ACCENT, RED = "#1b2a3a", "#6b7785", "#b8860b", "#c0392b"

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


def fractions(pH):
    r1 = 10 ** (pH - PK1)
    r2 = 10 ** (pH - PK2)
    d = 1 + r1 + r1 * r2
    return 1 / d, r1 / d, r1 * r2 / d


def alkalinity(pH, ct):
    a0, a1, a2 = fractions(pH)
    h = 10.0 ** -pH
    return ct * (a1 + 2 * a2) + KW / h - h


def solve_pH(ct, at, lo=2.0, hi=12.0):
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if alkalinity(mid, ct) > at:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def open_pH(pco2, at, lo=2.0, hi=12.0):
    """pH of a water with fixed alkalinity at gas equilibrium with pco2 (atm)."""
    co2 = KH * pco2
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        ct = co2 / fractions(mid)[0]
        if alkalinity(mid, ct) > at:
            hi = mid
        else:
            lo = mid
    ph = 0.5 * (lo + hi)
    return ph, co2 / fractions(ph)[0]


def save(fig, name):
    fig.savefig(OUT / name, format="svg", bbox_inches="tight", transparent=True)
    plt.close(fig)


# ---------------------------------------------------------------- numbers
for p in (2.8e-4, 4.0e-4, 4.2e-4):
    co2 = KH * p
    h = np.sqrt(10 ** -PK1 * co2 + KW)
    print(f"pure water at pCO2 {p:.1e} atm: CO2* {co2*1e6:.2f} umol/L, pH {-np.log10(h):.2f}")
co2 = KH * 4.00e-4
a0, a1, a2 = fractions(8.35)
CT835 = co2 / a0
print(f"pH 8.35: CT {CT835*1e6:.0f} umol/L; HCO3 {a1*CT835*1e6:.0f}, CO3 {a2*CT835*1e6:.1f}")

# ---------------------------------------------------------------- 1 Henry line
fig, ax = plt.subplots(figsize=(7.6, 4.8))
p = np.logspace(-4, -1, 50)
ax.plot(p, KH * p * 1e6, color=C_CO2, lw=3)
marks = [(2.8e-4, "pre-industrial\nair ≈ 280 ppm", (1.15e-4, 30)),
         (4.0e-4, "exercise value\n4.00×10$^{-4}$ atm", (8e-4, 4.5)),
         (1e-2, "soil air,\noften ~1%", (1.4e-3, 900))]
for pp, lab, xy in marks:
    ax.plot(pp, KH * pp * 1e6, "o", color=INK, ms=8, zorder=4)
    ax.annotate(lab + f"\n→ {KH*pp*1e6:.3g} µmol/L", (pp, KH * pp * 1e6), xytext=xy, fontsize=12.5,
                color=INK, arrowprops=dict(arrowstyle="-", color=GREY))
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("CO$_2$ partial pressure (atm)")
ax.set_ylabel("Dissolved CO$_2$* (µmol/L)")
ax.set_title("[CO$_2$*] = K$_H$ p$_{CO_2}$: ten times the gas, ten times dissolved", fontsize=15,
             color=INK, loc="left")
save(fig, "gases-henry.svg")

# ---------------------------------------------------------------- 2 CO2* versus C_T at pH 8.35
fig, ax = plt.subplots(figsize=(6.2, 4.8))
vals = [co2 * 1e6, a1 * CT835 * 1e6, a2 * CT835 * 1e6]
bottom = 0
for v, col, lab in zip(vals, (C_CO2, C_HCO3, C_CO3), ("CO$_2$*", "HCO$_3^-$", "CO$_3^{2-}$")):
    ax.bar(0, v, bottom=bottom, color=col, width=0.5)
    bottom += v
ax.bar(1.1, co2 * 1e6, color=C_CO2, width=0.5)
ax.text(1.1, co2 * 1e6 + 30, "13.6\nfrom Henry's law", ha="center", fontsize=14, color=C_CO2)
ax.text(0, bottom + 30, f"C$_T$ ≈ {bottom:.0f}", ha="center", fontsize=15, color=INK, fontweight="bold")
ax.text(0.3, 700, "HCO$_3^-$", color=C_HCO3, fontsize=16, fontweight="bold")
ax.set_xticks([0, 1.1], ["all dissolved\ninorganic C", "CO$_2$* only"])
ax.set_ylabel("µmol/L")
ax.set_ylim(0, 1600)
ax.set_title("Same water, pH 8.35", fontsize=16, color=INK, loc="left")
save(fig, "gases-ct-vs-co2.svg")

# ---------------------------------------------------------------- 3 CO2 uptake versus strong acid, Water A
CT_A, PH0 = 1.00e-3, 7.50
AT_A = alkalinity(PH0, CT_A)
q = np.linspace(0, 1.2e-3, 300)
ph_acid = [solve_pH(CT_A, AT_A - qq) for qq in q]
ph_co2 = [solve_pH(CT_A + qq, AT_A) for qq in q]
fig, ax = plt.subplots(figsize=(8.2, 4.8))
ax.plot(q * 1e3, ph_co2, color=C_CO2, lw=3, label="CO$_2$ added: C$_T$ up, A$_T$ fixed")
ax.plot(q * 1e3, ph_acid, color=RED, lw=3, label="strong acid added: C$_T$ fixed, A$_T$ down")
ax.set_xlim(0, 1.2)
ax.set_ylim(3.5, 8.0)
ax.set_xlabel("Amount added (mmol/L)")
ax.set_ylabel("Model pH")
ax.legend(frameon=False, loc="lower left", fontsize=13)
ax.set_title("Water A (pH 7.50, C$_T$ = 1.00 mmol/L), closed bottle", fontsize=15, color=INK, loc="left")
save(fig, "gases-co2-vs-acid.svg")
print(f"Water A + 1.0 mmol/L CO2: pH {solve_pH(CT_A + 1e-3, AT_A):.2f};"
      f" + 0.5: {solve_pH(CT_A + 0.5e-3, AT_A):.2f}; + 1.0 strong acid: {solve_pH(CT_A, AT_A - 1e-3):.2f}")

# ---------------------------------------------------------------- 4 C_T - A_T process diagram with pH contours
ct = np.linspace(0.2e-3, 3.0e-3, 220)
at = np.linspace(0.0, 3.0e-3, 220)
CT, AT = np.meshgrid(ct, at)
PHG = np.vectorize(solve_pH)(CT, AT)
fig, ax = plt.subplots(figsize=(8.4, 5.6))
cs = ax.contour(CT * 1e3, AT * 1e3, PHG, levels=[5, 6, 6.5, 7, 7.5, 8], colors=GREY,
                linewidths=1, linestyles=":")
ax.clabel(cs, fmt="pH %.1f", fontsize=11, inline_spacing=2)
x0, y0 = 1.4, 1.3
arrows = [(0.8, 0, C_CO2, "CO$_2$ in\n(respiration,\nuptake)", (0.45, 0.06), "left"),
          (-0.8, 0, C_CO2, "CO$_2$ out\n(degassing,\nphotosynthesis)", (-0.78, 0.06), "left"),
          (0, -0.8, RED, "strong acid", (0.06, -0.85), "left"),
          (0.4, 0.8, C_HCO3, "calcite dissolves\n(+1 C, +2 eq)", (0.43, 0.82), "left"),
          (-0.4, -0.8, C_CO3, "calcite\nprecipitates", (-0.45, -0.75), "right")]
for dx, dy, col, lab, (tx, ty), ha in arrows:
    ax.annotate("", (x0 + dx, y0 + dy), (x0, y0), arrowprops=dict(arrowstyle="-|>", color=col, lw=3,
                                                                    mutation_scale=22))
    ax.text(x0 + tx, y0 + ty, lab, color=col, fontsize=13, ha=ha, va="top" if dy < 0 else "bottom",
            bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
ax.plot(x0, y0, "o", color=INK, ms=10, zorder=5)
ax.set_xlim(0.2, 3.0)
ax.set_ylim(0, 3.0)
ax.set_xlabel("Total dissolved inorganic carbon C$_T$ (mmol/L)")
ax.set_ylabel("Alkalinity A$_T$ (meq/L)")
save(fig, "gases-process-map.svg")

# ---------------------------------------------------------------- 5 karst water degassing: pH and Omega
# Constructed: water that dissolved calcite to saturation under soil-air pCO2 = 0.01 atm
# (Ca = A_T / 2, no other ions), then degasses towards the atmosphere with no precipitation.
P_SOIL = 1e-2


def omega_at(pco2, at):
    ph, ctt = open_pH(pco2, at)
    return ph, ctt, (at / 2) * ctt * fractions(ph)[2] / KSP


lo, hi = 1e-5, 2e-2
for _ in range(100):
    mid = np.sqrt(lo * hi)
    if omega_at(P_SOIL, mid)[2] > 1:
        hi = mid
    else:
        lo = mid
AT_K = np.sqrt(lo * hi)
ph_s, ct_s, om_s = omega_at(P_SOIL, AT_K)
ph_a, ct_a, om_a = omega_at(4.0e-4, AT_K)
print(f"karst water: A_T {AT_K*1e3:.2f} meq/L, Ca {AT_K/2*1e3:.2f} mmol/L; soil pCO2 pH {ph_s:.2f}"
      f" Omega {om_s:.2f}; degassed to 4.0e-4 atm: pH {ph_a:.2f}, Omega {om_a:.1f}, C_T {ct_s*1e3:.2f}->{ct_a*1e3:.2f}")
pp = np.logspace(np.log10(4.0e-4), -2, 100)
res = np.array([omega_at(x, AT_K) for x in pp])
fig, ax = plt.subplots(figsize=(8.2, 4.8))
ax.plot(pp, res[:, 2], color=C_CO3, lw=3)
ax.axhline(1, color=GREY, ls=":", lw=1.5)
ax.text(1.5e-3, 0.85, "Ω = 1 (saturated)", ha="center", va="top", fontsize=13, color=GREY)
ax.set_ylim(0.5, 40)
ax.fill_between(pp, 1, res[:, 2], color=C_CO3, alpha=0.1)
for x, (ph, _, om), lab, xy in ((P_SOIL, (ph_s, 0, om_s), "in the soil", (7.0e-3, 0.55)),
                                (4.0e-4, (ph_a, 0, om_a), "at the surface", (6.0e-4, 6.5))):
    ax.plot(x, om, "o", color=INK, ms=9, zorder=4)
    ax.annotate(f"{lab}\npH {ph:.1f}, Ω ≈ {om:.2g}", (x, om), xytext=xy, fontsize=13, color=INK,
                arrowprops=dict(arrowstyle="-", color=GREY))
ax.set_xscale("log")
ax.set_yscale("log")
ax.invert_xaxis()
ax.set_xlabel("CO$_2$ partial pressure the water equilibrates with (atm)  →  degassing")
ax.set_ylabel("Calcite saturation Ω")
ax.set_title("Groundwater from limestone loses CO$_2$ (no calcite yet formed)", fontsize=15,
             color=INK, loc="left")
save(fig, "gases-degassing.svg")

# ---------------------------------------------------------------- 6 Omega versus pH at fixed Ca and C_T
ph = np.linspace(6.0, 9.5, 300)
CA, CT1 = 5.00e-4, 1.00e-3
om = CA * CT1 * fractions(ph)[2] / KSP
fig, ax = plt.subplots(figsize=(7.6, 4.6))
ax.plot(ph, om, color=C_CO3, lw=3)
ax.axhline(1, color=GREY, ls=":", lw=1.5)
ax.axhspan(1e-3, 1, color=C_CO2, alpha=0.07, lw=0)
ax.axhspan(1, 1e2, color=C_CO3, alpha=0.07, lw=0)
ax.text(6.1, 0.4, "undersaturated: calcite can dissolve", fontsize=13, color=C_CO2)
ax.text(6.1, 2.5, "supersaturated: calcite can form", fontsize=13, color=C_CO3)
ph1 = ph[np.argmin(abs(om - 1))]
ax.plot(ph1, 1, "o", color=INK, ms=8)
ax.annotate(f"Ω = 1 near pH {ph1:.1f}", (ph1, 1), xytext=(8.3, 0.08), fontsize=13, color=INK,
            arrowprops=dict(arrowstyle="-", color=GREY))
ax.set_yscale("log")
ax.set_ylim(1e-3, 1e2)
ax.set_xlabel("pH")
ax.set_ylabel("Calcite saturation Ω")
ax.set_title("Ca$^{2+}$ = 0.50 mmol/L, C$_T$ = 1.00 mmol/L", fontsize=15, color=INK, loc="left")
save(fig, "gases-omega-ph.svg")
print(f"Omega=1 at pH {ph1:.2f}; Omega at 7.5 {CA*CT1*fractions(7.5)[2]/KSP:.3f}, 8.3 {CA*CT1*fractions(8.3)[2]/KSP:.2f}")

print("wrote", sorted(p.name for p in OUT.glob("gases-*.svg")))
