"""Model figures for the aquatic composition lecture (aquatic-equilibria/lec.qmd).

Constructed teaching examples, not measured data. Ion tables match notes.qmd,
exercise.qmd and water-ions.csv. Activity coefficients use the Davies equation
(A = 0.509 at 25 degrees C), an estimate valid up to roughly I = 0.5 mol/L.
Run from the repository root:  python3 aquatic-equilibria/make_lec_figures.py
Writes SVG files to aquatic-equilibria/fig/ and prints the values quoted on slides.
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


CAT_COL = {"Ca$^{2+}$": "#8e9aaf", "Mg$^{2+}$": "#a9b4c2", "Na$^+$": "#c6cdd6"}
AN_COL = {"HCO$_3^-$": C_GREEN, "Cl$^-$": "#e8cf9f", "SO$_4^{2-}$": "#d9b26f"}

# ---------------------------------------------------------------- 1 worked ion balance
# notes.qmd worked example, mmol/L and charge
cations = [("Ca$^{2+}$", 0.500, 2), ("Mg$^{2+}$", 0.250, 2), ("Na$^+$", 0.500, 1)]
anions = [("HCO$_3^-$", 1.200, 1), ("Cl$^-$", 0.400, 1), ("SO$_4^{2-}$", 0.200, 2)]
fig, ax = plt.subplots(figsize=(6.4, 5.0))
for xi, ions, cols in ((0, cations, CAT_COL), (1, anions, AN_COL)):
    bottom = 0
    for name, c, z in ions:
        v = c * z
        ax.bar(xi, v, bottom=bottom, color=cols[name], width=0.58, edgecolor="white", lw=1.5)
        ax.text(xi, bottom + v / 2, f"{name}  {v:.3f}", ha="center", va="center", fontsize=14,
                color="white" if name == "HCO$_3^-$" else INK)
        bottom += v
    ax.text(xi, bottom + 0.05, f"total {bottom:.3f}", ha="center", fontsize=16, color=INK,
            fontweight="bold")
    print("worked balance side", xi, bottom)
ax.set_xticks([0, 1], ["cations", "anions"])
ax.set_ylabel("Charge (meq/L)")
ax.set_ylim(0, 2.35)
ax.set_title("Each column sums charge, not mass", fontsize=16, color=INK, loc="left")
save(fig, "ion-balance-worked.svg")

# ---------------------------------------------------------------- 2 balance check of samples A, B, C
# from water-ions.csv, raw (before the documented correction)
rows = [l.split(",") for l in (Path(__file__).resolve().parent / "water-ions.csv").read_text().split("\n")[1:] if l]
tot = {}
for sid, ion, mg, mm, z in rows:
    meq = float(mg) / float(mm) * abs(int(z))
    key = (sid, "cat" if int(z) > 0 else "an")
    tot[key] = tot.get(key, 0) + meq
fig, ax = plt.subplots(figsize=(7.2, 4.6))
for i, sid in enumerate("ABC"):
    cp, an = tot[(sid, "cat")], tot[(sid, "an")]
    imb = 100 * (cp - an) / (cp + an)
    print(f"sample {sid}: cations {cp:.3f} anions {an:.3f} meq/L imbalance {imb:+.2f}%")
    ax.bar(i - 0.17, cp, width=0.32, color="#8e9aaf", label="cations" if i == 0 else None)
    ax.bar(i + 0.17, an, width=0.32, color="#d9b26f", label="anions" if i == 0 else None)
    col = RED if abs(imb) > 1 else C_GREEN
    ax.text(i, max(cp, an) + 0.08, f"{imb:+.2f}%", ha="center", fontsize=16, color=col,
            fontweight="bold")
ax.set_xticks([0, 1, 2], ["Sample A", "Sample B", "Sample C"])
ax.set_ylabel("Charge sum (meq/L)")
ax.set_ylim(0, 2.45)
ax.legend(frameon=False, loc="upper center", ncol=2, fontsize=14, bbox_to_anchor=(0.5, 1.12))
save(fig, "balance-check.svg")

# ---------------------------------------------------------------- 3 activity coefficients (Davies)


def davies(I, z):
    s = np.sqrt(I)
    return 10 ** (-0.509 * z ** 2 * (s / (1 + s) - 0.3 * I))


I = np.logspace(-4, np.log10(0.2), 300)
fig, ax = plt.subplots(figsize=(9.6, 4.8))
bands = [(3e-4, 3e-3, "soft lake", C_BLUE), (3e-3, 2e-2, "hard river\nor lake", C_GREEN),
         (0.08, 0.2, "brackish\nBaltic", ACCENT)]
for lo, hi, lab, col in bands:
    ax.axvspan(lo, hi, color=col, alpha=0.12, lw=0)
    ax.text(np.sqrt(lo * hi), 1.04, lab, ha="center", va="bottom", fontsize=13, color=col)
ax.plot(I, davies(I, 1), color=INK, lw=3)
ax.plot(I, davies(I, 2), color=C_RUST, lw=3)
ax.text(0.025, 0.89, "z = 1 (Na$^+$, Cl$^-$, HCO$_3^-$)", fontsize=14, color=INK, va="bottom")
ax.text(1.1e-4, 0.70, "z = 2 (Ca$^{2+}$, SO$_4^{2-}$)", fontsize=14, color=C_RUST, va="top")
ax.text(0.19, 0.25, "Seawater (I ≈ 0.7) is off the chart:\nthis simple estimate no longer holds", fontsize=12,
        color=GREY, ha="right", va="bottom")
ax.plot(0.003, davies(0.003, 2), "o", color=C_RUST, ms=8)
ax.annotate(f"I = 0.003: γ ≈ {davies(0.003, 2):.2f}", (0.003, davies(0.003, 2)),
            xytext=(4e-4, 0.52), fontsize=13, color=C_RUST,
            arrowprops=dict(arrowstyle="->", color=C_RUST))
ax.set_xscale("log")
ax.set_xlim(1e-4, 0.22)
ax.set_ylim(0.2, 1.02)
ax.set_xlabel("Ionic strength I (mol/L)")
ax.set_ylabel("Activity coefficient γ")
ax.set_clip_on(False)
save(fig, "activity-coefficients.svg")
for i_, z in ((0.003, 1), (0.003, 2), (0.14, 1), (0.14, 2)):
    print(f"Davies gamma I={i_} z={z}: {davies(i_, z):.3f}")

# ---------------------------------------------------------------- 4 ionic strength contributions (exercise 3)
fig, ax = plt.subplots(figsize=(6.4, 4.4))
ions = [("Ca$^{2+}$", 1.00, 2, "#8e9aaf"), ("Cl$^-$", 2.00, 1, "#e8cf9f")]
x = np.arange(2)
for i, (n, c, z, col) in enumerate(ions):
    ax.bar(i - 0.18, c, width=0.34, color=col, edgecolor=INK, lw=1)
    ax.bar(i + 0.18, c * z ** 2, width=0.34, color=col, hatch="//", edgecolor=INK, lw=1)
    ax.text(i - 0.18, c + 0.08, f"{c:.2f}", ha="center", fontsize=14, color=INK)
    ax.text(i + 0.18, c * z ** 2 + 0.08, f"{c*z**2:.2f}", ha="center", fontsize=14, color=INK)
ax.set_xticks(x, [n for n, *_ in ions])
ax.set_ylabel("mmol/L")
ax.set_ylim(0, 4.8)
ax.bar(0, 0, color="white", edgecolor=INK, label="concentration c")
ax.bar(0, 0, color="white", edgecolor=INK, hatch="//", label="c · z$^2$")
ax.legend(frameon=False, fontsize=13, loc="upper right")
ax.set_title("I = ½ (4.00 + 2.00) = 3.00 mmol/L", fontsize=16, color=INK, loc="left")
save(fig, "ionic-strength.svg")

# ---------------------------------------------------------------- 5 generic acid distribution, pKa 5.00
pka = 5.00
pH = np.linspace(2, 8, 400)
fA = 1 / (1 + 10 ** (pka - pH))
fig, ax = plt.subplots(figsize=(7.4, 4.8))
ax.plot(pH, 1 - fA, color=C_BLUE, lw=3)
ax.plot(pH, fA, color=C_GREEN, lw=3)
ax.text(2.3, 0.88, "HA", color=C_BLUE, fontsize=19, fontweight="bold")
ax.text(7.2, 0.88, "A$^-$", color=C_GREEN, fontsize=19, fontweight="bold")
for p, lab, xy in ((pka - 1, "0.091", (2.2, 0.22)), (pka, "0.500", (5.3, 0.42)), (pka + 1, "0.909", (6.25, 0.66))):
    f = 1 / (1 + 10 ** (pka - p))
    ax.plot(p, f, "o", color=C_GREEN, ms=9, zorder=4)
    ax.annotate(f"pH {p:.2f}: A$^-$ = {lab}", (p, f), xytext=xy, fontsize=13, color=INK,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=1))
ax.axvline(pka, color=GREY, ls=":", lw=1.5)
ax.set_xlabel("Prescribed pH")
ax.set_ylabel("Fraction of total acid")
ax.set_ylim(0, 1.05)
ax.set_title("Weak acid with pK$_a$ = 5.00", fontsize=16, color=INK, loc="left")
save(fig, "acid-distribution.svg")
print("exercise 2: HA", 0.200 / 11, "A-", 0.200 * 10 / 11)

# ---------------------------------------------------------------- 5b worked split of a total (exercise 2)
fig, ax = plt.subplots(figsize=(6.0, 4.6))
ha_, a_ = 0.200 / 11, 0.200 * 10 / 11
ax.bar(0, a_, color=C_GREEN, width=0.5)
ax.bar(0, ha_, bottom=a_, color=C_BLUE, width=0.5)
ax.text(0, a_ / 2, f"A$^-$\n{a_:.4f}", ha="center", va="center", fontsize=16, color="white")
ax.annotate(f"HA {ha_:.5f}", (0.25, a_ + ha_ / 2), xytext=(0.45, 0.17), fontsize=16, color=C_BLUE,
            arrowprops=dict(arrowstyle="-", color=C_BLUE))
ax.text(0, 0.207, "total 0.200 mmol/L", ha="center", fontsize=14, color=INK)
ax.set_xlim(-0.6, 1.3)
ax.set_xticks([])
ax.spines["bottom"].set_visible(False)
ax.set_ylim(0, 0.235)
ax.set_ylabel("mmol/L")
ax.set_title("pK$_a$ 5.00, pH 6.00: split 1 : 10", fontsize=16, color=INK, loc="left")
save(fig, "acid-split.svg")

# ---------------------------------------------------------------- 6 ammonia: un-ionised fraction
pka_n = 9.25
pH = np.linspace(6, 10, 300)
f = 1 / (1 + 10 ** (pka_n - pH))
fig, ax = plt.subplots(figsize=(7.4, 4.8))
ax.axvspan(6.5, 8.5, color=C_GREEN, alpha=0.10, lw=0)
ax.text(7.5, 120, "typical rivers and lakes", ha="center", fontsize=13, color=C_GREEN)
ax.plot(pH, 100 * f, color=C_RUST, lw=3)
for p in (7.25, 8.25, 9.25):
    v = 100 / (1 + 10 ** (pka_n - p))
    ax.plot(p, v, "o", color=INK, ms=8, zorder=4)
    ax.annotate(f"{v:.2g}%", (p, v), xytext=(-12, 8), textcoords="offset points", ha="right",
                fontsize=14, color=INK)
ax.set_yscale("log")
ax.set_ylim(0.05, 200)
ax.set_xlabel("pH")
ax.set_ylabel("Un-ionised NH$_3$ (% of total)")
ax.set_title("NH$_4^+$ ⇌ NH$_3$ + H$^+$,  pK$_a$ ≈ 9.25 (25 °C)", fontsize=16, color=INK, loc="left")
save(fig, "ammonia-fraction.svg")

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
