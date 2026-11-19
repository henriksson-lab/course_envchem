"""Model figures for the waste and leachate lecture (waste-leachate/lec.qmd).

Constructed teaching illustrations, not measured data. Stoichiometry follows
notes.qmd: 4 H+ per FeS2 to Fe(OH)3, CaCO3 neutralising 2 H+ to the CO2* endpoint.
Run from the repository root:  python3 waste-leachate/make_lec_figures.py
Writes SVG files to waste-leachate/fig/ and prints the values quoted on slides.
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
M_FES2, M_CACO3 = 119.98, 100.09
n = 0.0100
print(f"worked: {4*n:.4f} eq acid, {2*n:.4f} mol SO4, {2*n:.4f} mol CaCO3 = {2*n*100:.2f} g (M=100)")
print(f"shortfall: 0.0150 mol CaCO3 neutralises {2*0.015:.4f} eq, residual {4*n-2*0.015:.4f} eq")
print(f"loads: A {10.0*2.00:.1f} mg/s, B {40.0*1.00:.1f} mg/s, B per year {40.0*3.156e7/1e9:.2f} t")
py = 0.01 * 1000e3 / M_FES2  # mol FeS2 in 1 t at 1 % pyrite
print(f"1 t waste, 1 % FeS2: {py:.1f} mol FeS2, {4*py:.0f} eq H+, {2*py:.0f} mol SO4, "
      f"CaCO3 {2*py*M_CACO3/1000:.1f} kg (2 eq/mol) or {4*py*M_CACO3/1000:.1f} kg (1 eq/mol)")

# ---------------------------------------------------------------- 1 acid budget, two cases
fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.6), sharey=True)
cases = (("Enough calcite: 0.0200 mol CaCO$_3$", 0.0200), ("Shortfall: 0.0150 mol CaCO$_3$", 0.0150))
for ax, (title, caco3) in zip(axes, cases):
    gen = 4 * n * 1e3
    neut = min(2 * caco3 * 1e3, gen)
    resid = gen - neut
    ax.bar(0, 2 * n * 1e3, color=RUST, width=0.6)
    ax.bar(0, 2 * n * 1e3, bottom=2 * n * 1e3, color="#d98b5f", width=0.6)
    ax.text(0, 10, "step 1", ha="center", va="center", color="white", fontsize=13)
    ax.text(0, 30, "step 2", ha="center", va="center", color="white", fontsize=13)
    ax.bar(1, neut, color=BLUE, width=0.6)
    ax.text(1, neut / 2, f"{neut:.0f}", ha="center", va="center", color="white", fontsize=16, fontweight="bold")
    ax.bar(2, resid, color=RED, width=0.6)
    ax.text(2, resid + 1.2, f"{resid:.0f}", ha="center", color=RED, fontsize=16, fontweight="bold")
    ax.text(0, gen + 1.2, f"{gen:.0f}", ha="center", color=INK, fontsize=16, fontweight="bold")
    ax.set_xticks([0, 1, 2], ["acid\ngenerated", "neutralised\nby calcite", "residual\nacid"])
    ax.set_title(title, fontsize=14, color=INK, loc="left")
    ax.set_ylim(0, 47)
axes[0].set_ylabel("mmol H$^+$ equivalents")
fig.text(0.5, -0.04, "0.0100 mol FeS$_2$ oxidised completely; CO$_2$* endpoint (2 eq per CaCO$_3$). Rates and access ignored.",
         ha="center", fontsize=12, color=GREY)
fig.tight_layout()
save(fig, "acid-budget.svg")

# ---------------------------------------------------------------- 2 lag time: cumulative acid vs neutralisation capacity
# Constructed: 1 t waste, 1 % pyrite (333 eq potential), calcite capacity 150 eq,
# pyrite oxidation first order with k = 0.02 per year (illustrative only).
t = np.linspace(0, 120, 600)
ap, npot, k = 4 * py, 150.0, 0.02
cum = ap * (1 - np.exp(-k * t))
t_cross = -np.log(1 - npot / ap) / k
print(f"lag model: AP {ap:.0f} eq, NP {npot:.0f} eq, calcite exhausted at {t_cross:.0f} years")
fig, ax = plt.subplots(figsize=(9.0, 4.8))
ax.plot(t, cum, color=RED, lw=3, label="acid generated (cumulative)")
ax.axhline(npot, color=BLUE, lw=3, ls="--", label="calcite neutralising capacity")
ax.axhline(ap, color=GREY, lw=1.5, ls=":")
ax.text(40, ap + 8, f"acid potential if all pyrite reacts: {ap:.0f} eq", color=GREY, fontsize=13)
ax.fill_between(t, npot, cum, where=cum > npot, color=RED, alpha=0.15)
ax.axvline(t_cross, color=INK, lw=1.2)
ax.text(t_cross + 2, 40, f"≈ {t_cross:.0f} years:\ncalcite used up,\nacid drainage starts", fontsize=13, color=INK)
ax.text(1.5, 230, "first 30 years:\nneutral\ndrainage, but\nacid is\nbeing made", fontsize=12.5, color=BLUE)
ax.set_xlabel("Years since the waste was exposed")
ax.set_ylabel("H$^+$ equivalents per tonne")
ax.set_xlim(0, 120)
ax.set_ylim(0, 380)
ax.legend(frameon=False, loc="lower right", fontsize=13)
ax.set_title("Constructed: 1 t waste, 1 % pyrite, rate chosen for illustration", fontsize=13,
             color=GREY, loc="left")
save(fig, "lag-time.svg")

# ---------------------------------------------------------------- 3 concentration vs load
fig, axes = plt.subplots(1, 2, figsize=(7.4, 4.2))
names = ["A\n10 L/s", "B\n40 L/s"]
axes[0].bar(names, [2.00, 1.00], color=[ACCENT, BLUE], width=0.55)
axes[0].set_ylabel("Dissolved Fe (mg/L)")
axes[0].set_title("Concentration", fontsize=15, color=INK, loc="left")
axes[0].set_ylim(0, 2.5)
for i, v in enumerate([2.00, 1.00]):
    axes[0].text(i, v + 0.06, f"{v:.2f}", ha="center", fontsize=15, color=INK)
axes[1].bar(names, [20.0, 40.0], color=[ACCENT, BLUE], width=0.55)
axes[1].set_ylabel("Fe load (mg/s)")
axes[1].set_title("Load = flow × concentration", fontsize=15, color=INK, loc="left")
axes[1].set_ylim(0, 50)
for i, v in enumerate([20.0, 40.0]):
    axes[1].text(i, v + 1.2, f"{v:.0f}", ha="center", fontsize=15, color=INK)
fig.tight_layout()
save(fig, "load-vs-concentration.svg")

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
