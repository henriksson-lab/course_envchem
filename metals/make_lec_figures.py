"""Model figures for the metals lecture (metals/lec.qmd).

Constructed teaching-model predictions, not measured data: dilute water at
25 degrees C, concentrations used in place of activities. The fictitious metal M
uses the constants in notes.qmd and exercise.qmd. The aluminium curves use
approximate literature constants (gibbsite solubility and Al hydrolysis) and are
for interpretation only.
Run from the repository root:  python3 metals/make_lec_figures.py
Writes SVG files to metals/fig/ and prints the values quoted on slides.
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
BROWN = "#8a5a2b"

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
BETA, MT = 1.00e6, 2.00          # L/mol, umol/L
for L in (1.00e-5, 1.00e-6):
    free = MT / (1 + BETA * L)
    print(f"[L]={L:.0e}: beta[L]={BETA*L:.2f}, free M={free:.4f}, ML={MT-free:.4f} umol/L")
KSP, OH = 1.00e-16, 1.00e-5
msat = KSP / OH**2 * 1e6
print(f"free-ion saturation at pH 9: {msat:.3f} umol/L")
print(f"total 10 umol/L, beta[L]=9: free {10/(1+9):.3f} umol/L; no ligand: Omega={10/msat:.1f}")

# ---------------------------------------------------------------- 1 free fraction vs free ligand
fig, ax = plt.subplots(figsize=(7.4, 4.7))
logL = np.linspace(-9, -3, 400)
ff = 1 / (1 + BETA * 10**logL)
ax.plot(logL, ff, color=BLUE, lw=3.2)
for L, lab, dx in ((1e-6, "β[L] = 1\nhalf free", 0.25), (1e-5, "β[L] = 10\n9.1 % free", 0.25)):
    f = 1 / (1 + BETA * L)
    ax.plot(np.log10(L), f, "o", ms=10, mfc="white", mec=INK, mew=2, zorder=4)
    ax.annotate(lab, (np.log10(L), f), xytext=(np.log10(L) + dx, f + 0.18), fontsize=14,
                color=INK, arrowprops=dict(arrowstyle="->", color=INK))
ax.set_xticks(range(-9, -2), [f"10$^{{{k}}}$" for k in range(-9, -2)])
ax.set_xlabel("Free ligand [L] (mol/L)")
ax.set_ylabel("Fraction of M$_T$ that is free M")
ax.set_ylim(0, 1.08)
ax.set_title("One complex, β = 10$^6$ L/mol", fontsize=16, color=INK, loc="left")
save(fig, "binding-fraction.svg")

# ---------------------------------------------------------------- 2 worked split (two ligand levels)
fig, ax = plt.subplots(figsize=(6.2, 4.7))
cases = [("[L] = 10$^{-5}$ M", 1e-5), ("[L] = 10$^{-6}$ M", 1e-6)]
POS = [0, 1.25]
for i, (lab, L) in zip(POS, cases):
    free = MT / (1 + BETA * L)
    ax.bar(i, free, color=RED, width=0.55)
    ax.bar(i, MT - free, bottom=free, color=BLUE, width=0.55)
    fl, ml = ("0.1818", "1.818") if L > 5e-6 else ("1.00", "1.00")
    ax.text(i + 0.32, max(free / 2, 0.12), f"free {fl}", va="center", fontsize=14, color=RED, zorder=5)
    ax.text(i + 0.32, free + (MT - free) / 2, f"ML {ml}", va="center", fontsize=14, color=BLUE, zorder=5)
ax.set_xticks(POS, [c[0] for c in cases])
ax.set_xlim(-0.45, 2.3)
ax.set_ylim(0, 2.3)
ax.axhline(MT, color=GREY, ls=":", lw=1.5)
ax.text(2.25, MT + 0.05, "M$_T$ = 2.00", ha="right", fontsize=13, color=GREY)
ax.set_ylabel("µmol/L")
ax.set_title("Same total, different free metal", fontsize=16, color=INK, loc="left")
save(fig, "worked-split.svg")

# ---------------------------------------------------------------- 3 ligand balance check
fig, ax = plt.subplots(figsize=(6.4, 4.5))
vals = [("M$_T$", 2.00, GREY), ("claimed ML", 1.818, RED), ("L$_T$", 0.500, GREEN)]
for i, (lab, v, col) in enumerate(vals):
    ax.bar(i, v, color=col, width=0.6)
    ax.text(i, v + 0.05, {2.0: "2.00", 1.818: "1.818", 0.5: "0.500"}[v], ha="center", fontsize=15, color=INK)
ax.axhline(0.5, color=GREEN, ls="--", lw=1.5)
ax.text(2.0, 1.1, "ML can never\nexceed L$_T$", fontsize=14, color=GREEN, ha="center", va="bottom")
ax.set_xticks(range(3), [v[0] for v in vals])
ax.set_ylabel("µmol/L")
ax.set_ylim(0, 2.35)
ax.set_title("Each ML uses one ligand", fontsize=16, color=INK, loc="left")
save(fig, "ligand-check.svg")

# ---------------------------------------------------------------- 4 aluminium solubility (gibbsite)
# Approximate 25 C constants: Al(OH)3(s) + 3H+ = Al3+ + 3H2O, log K ~ 9.35 (microcrystalline gibbsite);
# Al3+ hydrolysis log beta_n (with release of n H+): -5.0, -10.1, -16.9, -22.7.
pH = np.linspace(3.5, 9.5, 600)
h = 10.0 ** -pH
al3 = 10 ** (9.35) * h**3
species = [("Al$^{3+}$", al3, RED),
           ("AlOH$^{2+}$", al3 * 10**-5.0 / h, RUST),
           ("Al(OH)$_2^+$", al3 * 10**-10.1 / h**2, ACCENT),
           ("Al(OH)$_3$(aq)", al3 * 10**-16.9 / h**3, GREY),
           ("Al(OH)$_4^-$", al3 * 10**-22.7 / h**4, BLUE)]
tot = sum(s[1] for s in species)
imin = np.argmin(tot)
print(f"gibbsite minimum: pH {pH[imin]:.2f}, total Al {tot[imin]*1e6:.3f} umol/L; "
      f"at pH 5.0: {np.interp(5.0, pH, tot)*1e6:.1f} umol/L; pH 4.5: {np.interp(4.5, pH, tot)*1e6:.0f}")
fig, ax = plt.subplots(figsize=(9.4, 5.0))
ax.axvspan(4.3, 5.5, color=RED, alpha=0.09, lw=0)
ax.text(4.9, 2.85, "acidified\nlakes", ha="center", va="top", fontsize=13, color=RED)
shown = {"Al$^{3+}$": (5.72, -1.25), "AlOH$^{2+}$": (6.4, -2.2), "Al(OH)$_4^-$": (8.35, -0.25)}
for lab, y, col in species:
    if lab in shown:
        ax.plot(pH, np.log10(y * 1e6), color=col, lw=2, ls="--")
        ax.text(*shown[lab], lab, color=col, fontsize=15, fontweight="bold")
ax.plot(pH, np.log10(tot * 1e6), color=INK, lw=3.4)
ax.annotate("total dissolved Al:\nminimum near pH 6", (pH[imin], np.log10(tot[imin] * 1e6)),
            xytext=(6.9, 1.7), ha="left", fontsize=14, color=INK,
            arrowprops=dict(arrowstyle="->", color=INK))
ax.set_xlim(3.5, 9.5)
ax.set_ylim(-3, 3)
ax.set_yticks(range(-3, 4), ["0.001", "0.01", "0.1", "1", "10", "100", "1000"])
ax.set_xlabel("pH")
ax.set_ylabel("Dissolved Al (µmol/L)")
fig.text(0.5, -0.1, "Solid: total Al in equilibrium with microcrystalline Al(OH)$_3$(s); dashed: main species.\nApproximate 25 °C constants; F$^-$, SO$_4^{2-}$ and organic ligands omitted.",
         ha="center", fontsize=12, color=GREY)
save(fig, "al-solubility.svg")

# ---------------------------------------------------------------- 5 complexation raises the dissolved total at saturation
fig, ax = plt.subplots(figsize=(7.6, 4.9))
pH2 = np.linspace(7.5, 10.5, 200)
oh = 10.0 ** (pH2 - 14)
for bl, col in ((0, RED), (9, BLUE), (99, GREEN)):
    ax.plot(pH2, KSP / oh**2 * (1 + bl) * 1e6, color=col, lw=3)
    ax.text(10.52, KSP / 10**(-3.5 * 2) * (1 + bl) * 1e6, f" β[L] = {bl}", color=col, fontsize=14, va="center")
ax.plot(9.0, 10.0, "o", ms=10, mfc="white", mec=INK, mew=2, zorder=4)
ax.annotate("total 10 µmol/L at pH 9:\nsaturated only if β[L] = 9", (9.0, 10.0), xytext=(7.6, 0.02),
            fontsize=13, color=INK, arrowprops=dict(arrowstyle="->", color=INK))
ax.set_yscale("log")
ax.set_xlabel("pH")
ax.set_ylabel("Dissolved M$_T$ at saturation (µmol/L)")
ax.set_title("Fictitious M(OH)$_2$, K$_{sp}$ = 10$^{-16}$", fontsize=16, color=INK, loc="left")
save(fig, "saturation-total.svg")

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
