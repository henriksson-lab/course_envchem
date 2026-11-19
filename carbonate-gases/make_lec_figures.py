"""Model figures for the carbonate lecture (carbonate-gases/lec.qmd).

Constructed teaching-model predictions, not measured data: 25 degrees C, dilute
freshwater, closed carbonate system, constants from reference.qmd.
Run from the repository root:  python3 carbonate-gases/make_lec_figures.py
Writes SVG files to carbonate-gases/fig/ and prints the values quoted on slides.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PK1, PK2, KW = 6.35, 10.33, 1.0e-14
OUT = Path(__file__).resolve().parent / "fig"
OUT.mkdir(exist_ok=True)

C_CO2, C_HCO3, C_CO3 = "#2468A0", "#25713E", "#AD4825"
INK, GREY, ACCENT = "#1b2a3a", "#6b7785", "#b8860b"
WATER_A, WATER_B = "#2468A0", "#AD4825"

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
    """Carbonate alkalinity in mol/L for total carbon ct (mol/L)."""
    a0, a1, a2 = fractions(pH)
    h = 10.0 ** -pH
    return ct * (a1 + 2 * a2) + KW / h - h


def solve_pH(ct, at, lo=2.0, hi=12.0):
    """Bisection: alkalinity increases monotonically with pH at fixed ct."""
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if alkalinity(mid, ct) > at:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def buffer_capacity(pH, ct):
    a0, a1, a2 = fractions(pH)
    h = 10.0 ** -pH
    return np.log(10) * (h + KW / h + ct * (a0 * a1 + a1 * a2 + 4 * a0 * a2))


def save(fig, name):
    fig.savefig(OUT / name, format="svg", bbox_inches="tight", transparent=True)
    plt.close(fig)


def species_legend(ax, x=0.98, y=0.5, ha="right"):
    for i, (lab, col) in enumerate([("CO$_2$*", C_CO2), ("HCO$_3^-$", C_HCO3),
                                    ("CO$_3^{2-}$", C_CO3)]):
        ax.text(x, y - 0.1 * i, lab, color=col, transform=ax.transAxes,
                ha=ha, va="center", fontsize=17, fontweight="bold")


# ---------------------------------------------------------------- numbers
CT_A, CT_B, PH0, DOSE = 1.00e-3, 0.100e-3, 7.50, 0.050e-3
AT_A, AT_B = alkalinity(PH0, CT_A), alkalinity(PH0, CT_B)
PH_A = solve_pH(CT_A, AT_A - DOSE)
PH_B = solve_pH(CT_B, AT_B - DOSE)
print(f"Water A: A_T {AT_A*1e3:.4f} -> {(AT_A-DOSE)*1e3:.4f} meq/L, pH {PH_A:.3f}")
print(f"Water B: A_T {AT_B*1e3:.4f} -> {(AT_B-DOSE)*1e3:.4f} meq/L, pH {PH_B:.3f}")
print("fractions at pH 8.35:", [round(f, 5) for f in fractions(8.35)])
print("fractions at pH 7.50:", [round(f, 4) for f in fractions(7.50)])
for ct in (CT_A, CT_B):
    print(f"beta at 7.50, C_T={ct*1e3:.2f} mM: {buffer_capacity(7.5, ct)*1e3:.4f} meq/L per pH")

pH = np.linspace(3.5, 12.5, 901)
a0, a1, a2 = fractions(pH)

# ---------------------------------------------------------------- 1 ratio line
fig, ax = plt.subplots(figsize=(6.4, 4.6))
x = np.linspace(4.35, 9.35, 50)
ax.plot(x, x - PK1, color=C_HCO3, lw=3)
for p in (5.35, 6.35, 7.35, 8.35):
    ax.plot(p, p - PK1, "o", color=INK, ms=8, zorder=3)
    ratio = 10 ** (p - PK1)
    lab = {0.1: "1 : 10", 1: "1 : 1", 10: "10 : 1", 100: "100 : 1"}[round(ratio, 1) if ratio < 1 else round(ratio)]
    ax.annotate(lab, (p, p - PK1), xytext=(-14, 12), textcoords="offset points",
                ha="right", fontsize=15, color=INK)
ax.axvline(PK1, color=GREY, ls=":", lw=1.5)
ax.text(PK1 - 0.1, 2.6, "pH = pK$_1$", color=GREY, fontsize=14, ha="right")
ax.set_xlabel("pH")
ax.set_ylabel("log$_{10}$ ( [HCO$_3^-$] / [CO$_2$*] )")
ax.set_yticks([-2, -1, 0, 1, 2, 3])
ax.set_title("One pH unit = a factor of ten", fontsize=16, color=INK, loc="left")
save(fig, "ratio-line.svg")

# ---------------------------------------------------------------- 2 fractions at 8.35
f = fractions(8.35)
fig, ax = plt.subplots(figsize=(6.4, 4.4))
labels = ["CO$_2$*", "HCO$_3^-$", "CO$_3^{2-}$"]
bars = ax.bar(labels, f, color=[C_CO2, C_HCO3, C_CO3], width=0.62)
for b, v in zip(bars, f):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.4f}", ha="center",
            fontsize=16, color=INK)
ax.set_ylim(0, 1.12)
ax.set_ylabel("Fraction of C$_T$")
ax.set_title("pH 8.35: proportions 1 : 100 : 1.047", fontsize=16, color=INK, loc="left")
save(fig, "fractions-835.svg")

# ---------------------------------------------------------------- 3 annotated distribution
fig, ax = plt.subplots(figsize=(10, 4.9))
for y, col in ((a0, C_CO2), (a1, C_HCO3), (a2, C_CO3)):
    ax.plot(pH, y, color=col, lw=3.2)
for pk in (PK1, PK2):
    ax.axvline(pk, color=GREY, ls=":", lw=1.5)
    ax.plot(pk, 0.5, "o", ms=9, mfc="white", mec=INK, mew=2, zorder=4)
ax.annotate("pH = pK$_1$ = 6.35\nCO$_2$* = HCO$_3^-$", (PK1, 0.5), xytext=(4.0, 0.62),
            fontsize=14, color=INK, arrowprops=dict(arrowstyle="->", color=INK))
ax.annotate("pH = pK$_2$ = 10.33\nHCO$_3^-$ = CO$_3^{2-}$", (PK2, 0.5), xytext=(7.5, 0.60),
            fontsize=14, color=INK, arrowprops=dict(arrowstyle="->", color=INK))
ax.text(4.3, 0.9, "CO$_2$*", color=C_CO2, fontsize=19, fontweight="bold")
ax.text(7.75, 0.9, "HCO$_3^-$", color=C_HCO3, fontsize=19, fontweight="bold")
ax.text(11.45, 0.55, "CO$_3^{2-}$", color=C_CO3, fontsize=19, fontweight="bold")
ax.set_xlim(3.5, 12.5)
ax.set_ylim(0, 1.03)
ax.set_xlabel("Prescribed pH")
ax.set_ylabel("Fraction of C$_T$")
save(fig, "speciation-annotated.svg")

# ---------------------------------------------------------------- 4 real waters
fig, ax = plt.subplots(figsize=(10, 5.0))
bands = [
    (4.3, 5.5, "acidified\nsoft-water lake", "#c0392b"),
    (5.5, 5.7, "clean\nrain", "#7f8c8d"),
    (6.5, 8.3, "most rivers\nand lakes", C_HCO3),
    (8.0, 8.2, "surface\nseawater", C_CO2),
]
ytxt = [1.07, 1.19, 1.07, 1.19]
for (lo, hi, lab, col), yt in zip(bands, ytxt):
    ax.axvspan(lo, hi, color=col, alpha=0.13, lw=0)
    ax.text((lo + hi) / 2, yt, lab, ha="center", va="bottom", fontsize=13, color=col)
for y, col in ((a0, C_CO2), (a1, C_HCO3), (a2, C_CO3)):
    ax.plot(pH, y, color=col, lw=3)
species_legend(ax, x=0.985, y=0.55)
ax.set_xlim(3.5, 12.5)
ax.set_ylim(0, 1.05)
ax.set_xlabel("pH")
ax.set_ylabel("Fraction of C$_T$")
ax.set_clip_on(False)
save(fig, "real-waters.svg")

# ---------------------------------------------------------------- 5 fraction vs amount
fa = fractions(PH0)
fig, ax = plt.subplots(figsize=(6.6, 4.8))
for i, (ct, name) in enumerate(((CT_A, "Water A"), (CT_B, "Water B"))):
    bottom = 0
    for v, col in zip(fa, (C_CO2, C_HCO3, C_CO3)):
        ax.bar(i, v * ct * 1e3, bottom=bottom, color=col, width=0.55)
        bottom += v * ct * 1e3
    ax.text(i, bottom + 0.03, f"C$_T$ = {ct*1e3:.3g} mmol/L", ha="center", fontsize=14, color=INK)
ax.set_xticks([0, 1], ["Water A", "Water B"])
ax.set_ylabel("Concentration (mmol/L)")
ax.set_ylim(0, 1.18)
ax.set_title("Same pH 7.50, same fractions", fontsize=16, color=INK, loc="left")
species_legend(ax, x=0.99, y=0.72)
save(fig, "fraction-vs-amount.svg")

# ---------------------------------------------------------------- 6 ion balance of two lakes
# Constructed ion compositions (micro-eq/L) in the range of soft-water and hard-water lakes.
granite = {"cat": [("Ca$^{2+}$", 70), ("Mg$^{2+}$", 30), ("Na$^+$", 90), ("K$^+$", 10), ("H$^+$", 10)],
           "an": [("SO$_4^{2-}$", 110), ("Cl$^-$", 90), ("NO$_3^-$", 5), ("HCO$_3^-$", 5)]}
lime = {"cat": [("Ca$^{2+}$", 1800), ("Mg$^{2+}$", 300), ("Na$^+$", 150), ("K$^+$", 30)],
        "an": [("SO$_4^{2-}$", 200), ("Cl$^-$", 150), ("NO$_3^-$", 30), ("HCO$_3^-$", 1900)]}
cols = {"Ca$^{2+}$": "#8e9aaf", "Mg$^{2+}$": "#a9b4c2", "Na$^+$": "#c6cdd6", "K$^+$": "#dde2e8",
        "H$^+$": "#c0392b", "SO$_4^{2-}$": "#d9b26f", "Cl$^-$": "#e8cf9f", "NO$_3^-$": "#f2e3c4",
        "HCO$_3^-$": C_HCO3}
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8))
for ax, lake, title in ((axes[0], granite, "Lake on granite"), (axes[1], lime, "Lake on limestone")):
    for xi, side in ((0, "cat"), (1, "an")):
        bottom = 0
        for name, v in lake[side]:
            ax.bar(xi, v, bottom=bottom, color=cols[name], width=0.6, edgecolor="white", lw=1)
            if v / sum(w for _, w in lake[side]) > 0.06:
                ax.text(xi, bottom + v / 2, name, ha="center", va="center", fontsize=14,
                        color="white" if name in ("HCO$_3^-$", "H$^+$") else INK)
            bottom += v
    ax.set_xticks([0, 1], ["cations", "anions"])
    ax.set_title(title, fontsize=17, color=INK, loc="left")
    ax.set_ylabel("µeq/L")
axes[0].annotate("HCO$_3^-$ ≈ 5\nH$^+$ ≈ 10", (1.32, 205), xytext=(1.0, 240), fontsize=14,
                 color=INK, ha="center", annotation_clip=False)
axes[0].set_ylim(0, 290)
axes[1].set_ylim(0, 2550)
fig.text(0.5, -0.04, "Note the different scales. Constructed compositions; each column sums to the same charge.",
         ha="center", fontsize=12, color=GREY)
fig.tight_layout()
save(fig, "ion-balance-lakes.svg")

# ---------------------------------------------------------------- 7 buffer capacity
fig, ax = plt.subplots(figsize=(7.2, 4.6))
pb = np.linspace(4, 11.5, 600)
for ct, col, lab in ((CT_A, WATER_A, "C$_T$ = 1.00 mmol/L (A)"), (CT_B, WATER_B, "C$_T$ = 0.100 mmol/L (B)")):
    ax.plot(pb, buffer_capacity(pb, ct) * 1e3, color=col, lw=3, label=lab)
ax.axvline(PH0, color=GREY, ls=":", lw=1.5)
ax.text(PH0 + 0.08, 1.15, "pH 7.50", color=GREY, fontsize=13)
ax.set_yscale("log")
ax.set_ylim(5e-3, 2)
ax.set_xlabel("pH")
ax.set_ylabel("Buffer capacity β\n(meq/L per pH unit)")
ax.legend(frameon=False, fontsize=13, loc="lower right")
save(fig, "buffer-capacity.svg")

# ---------------------------------------------------------------- 8 alkalinity vs pH, reading the new pH
fig, ax = plt.subplots(figsize=(7.6, 5.0))
pa = np.linspace(5.6, 8.4, 400)
for ct, at, ph1, col, name in ((CT_A, AT_A, PH_A, WATER_A, "A"), (CT_B, AT_B, PH_B, WATER_B, "B")):
    ax.plot(pa, alkalinity(pa, ct) * 1e3, color=col, lw=3)
    ax.text(8.42, alkalinity(8.4, ct) * 1e3, f" Water {name}", color=col, fontsize=15, va="center")
    for p, a in ((PH0, at), (ph1, at - DOSE)):
        ax.plot([5.6, p], [a * 1e3] * 2, color=col, lw=1.2, ls="--")
        ax.plot([p, p], [1e-2, a * 1e3], color=col, lw=1.2, ls="--")
        ax.plot(p, a * 1e3, "o", color=col, ms=8)
    ax.annotate("", (ph1, (at - DOSE) * 1e3), (PH0, at * 1e3),
                arrowprops=dict(arrowstyle="->", color=INK, lw=2))
ax.set_yscale("log")
ax.set_xlim(5.6, 8.4)
ax.set_ylim(1e-2, 3)
ax.set_xlabel("pH")
ax.set_ylabel("Alkalinity A$_T$ (meq/L)")
ax.set_title("Fixed C$_T$: each alkalinity has one pH", fontsize=16, color=INK, loc="left")
save(fig, "alkalinity-reading.svg")

# ---------------------------------------------------------------- 9 titration curves
fig, ax = plt.subplots(figsize=(8.0, 4.8))
q = np.linspace(0, 1.2e-3, 400)
for ct, at, col, name in ((CT_A, AT_A, WATER_A, "Water A"), (CT_B, AT_B, WATER_B, "Water B")):
    ph = [solve_pH(ct, at - qq) for qq in q]
    ax.plot(q * 1e3, ph, color=col, lw=3, label=name)
ax.axvline(DOSE * 1e3, color=GREY, ls=":", lw=1.5)
ax.text(DOSE * 1e3 + 0.02, 7.85, "0.050 mmol/L\nstrong acid", color=GREY, fontsize=12)
ax.axhspan(3.5, 5.5, color="#c0392b", alpha=0.08, lw=0)
ax.text(0.3, 4.75, "pH < 5.5: harmful to many fish\nand invertebrates", ha="left", va="top",
        fontsize=12, color="#c0392b")
ax.set_xlim(0, 1.2)
ax.set_ylim(3.5, 8.0)
ax.set_xlabel("Strong acid added (mmol/L)")
ax.set_ylabel("Model pH")
ax.legend(frameon=False, loc="upper right", fontsize=14, bbox_to_anchor=(1.0, 0.82))
save(fig, "titration.svg")

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
