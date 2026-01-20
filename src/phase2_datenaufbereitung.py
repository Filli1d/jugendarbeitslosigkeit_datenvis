"""
Visualisierung

Input:
- data/clean_long.csv 

Output:
- figures/01_line_jugend_vs_gesamt.png
- figures/02_heatmap_jugendquote.png
- figures/03_slopegraph_jugendquote.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

#Pfade
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(BASE_DIR, "data", "clean", "clean_long.csv")
FIG_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

print("Projektordner:", BASE_DIR)
print("Lade:", CLEAN_PATH)

# Style
mpl.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 250,
    "font.size": 12,
    "axes.titlesize": 16,
    "axes.labelsize": 13,
    "legend.fontsize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
})

COLOR_YOUTH = "#1f77b4"   # Blau (Jugend)
COLOR_TOTAL = "#7f7f7f"   # Grau (Gesamt/Referenz)

def beautify(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

def save_fig(fig, filename):
    fig.savefig(os.path.join(FIG_DIR, filename))
    plt.close(fig)



#Daten laden

df_long = pd.read_csv(CLEAN_PATH)

VAR_TOTAL = "Arbeitslosenquote"
VAR_YOUTH = "Arbeitslosenquote Jüngere"

df_long = df_long[df_long["variable"].isin([VAR_TOTAL, VAR_YOUTH])].copy()

#ChatGPT:
#Erzeuge mir lauffähigen Python-Code (pandas + matplotlib) für ein Uni-Projekt zur Datenvisualisierung. 
#Ich habe dir eine Datendatei gegeben, die du selbst einlesen und inspizieren sollst, um zu erkennen, 
#welche Spalten enthalten sind und wie die Daten strukturiert sind. 
#Der Code soll ausschließlich Visualisierungen erzeugen, sauber kommentiert sein und jede Grafik exportieren.
#Nutze klare Abschnitts-Kommentare, damit sofort erkennbar ist, welche Visualisierung erstellt wird.
#Der Code MUSS folgende Visualisierungen enthalten:
#1) Ein Liniendiagramm mit zwei Zeitreihen (Jugendarbeitslosigkeit vs. Gesamt), aggregiert über Regionen,
#mit klarer Aussage, dass Jugendarbeitslosigkeit stärker auf Krisen reagiert.
#2) Eine Heatmap (Region × Jahr) für Jugendarbeitslosigkeit, mit nach Durchschnitt sortierten Regionen
#und gut lesbarer Farbskala.
#3) Einen Hotspot-Vergleich zweier Jahre (z. B. 2019 → 2023) für ausgewählte Regionen,
#inklusive einer explizit hervorgehobenen Region wie „Nürnberg“, dargestellt als Linien.
#4) Ein horizontales Balkendiagramm, das die Veränderung der Jugendarbeitslosigkeit in Prozentpunkten zeigt
#(negativ = besser, positiv = schlechter), visuell klar getrennt.

Gib ausschließlich Python-Code aus, ohne erklärenden Text außerhalb des Codes.

# ============================================================
# 1) LINE: Jugend vs Gesamt 
# ============================================================
df_line = df_long.groupby(["jahr", "variable"], as_index=False)["value"].mean()

fig, ax = plt.subplots(figsize=(9, 5))

sub_total = df_line[df_line["variable"] == VAR_TOTAL]
ax.plot(sub_total["jahr"], sub_total["value"],
        marker="o", linewidth=2.5, color=COLOR_TOTAL, alpha=0.9,
        label="Arbeitslosenquote gesamt")

sub_youth = df_line[df_line["variable"] == VAR_YOUTH]
ax.plot(sub_youth["jahr"], sub_youth["value"],
        marker="o", linewidth=3.5, color=COLOR_YOUTH,
        label="Arbeitslosenquote Jüngere")

ax.set_title("Jugendarbeitslosigkeit reagiert stärker auf Krisen (Mittel über Regionen)", pad=12)
ax.set_xlabel("Jahr")
ax.set_ylabel("Arbeitslosenquote (%)")
ax.legend(loc="upper right")
beautify(ax)

fig.tight_layout()
save_fig(fig, "01_line_jugend_vs_gesamt.png")

# ============================================================
# 2) HEATMAP: Region × Jahr 
# ============================================================
df_heat = df_long[df_long["variable"] == VAR_YOUTH].copy()
pivot_h = df_heat.pivot_table(index="region", columns="jahr", values="value", aggfunc="mean")

pivot_h["mean"] = pivot_h.mean(axis=1)
pivot_h = pivot_h.sort_values("mean", ascending=False).drop(columns=["mean"])

vmin = float(np.nanmin(pivot_h.values))
vmax = float(np.nanmax(pivot_h.values))

fig, ax = plt.subplots(figsize=(11.5, 6.5))
im = ax.imshow(pivot_h.values, aspect="auto", vmin=vmin, vmax=vmax, cmap="cividis")

ax.set_title("Wo ist Jugendarbeitslosigkeit dauerhaft höher? (Region × Jahr)", pad=12)
ax.set_xlabel("Jahr")
ax.set_ylabel("Region (sortiert nach Durchschnitt)")

ax.set_xticks(np.arange(len(pivot_h.columns)))
ax.set_xticklabels(pivot_h.columns, rotation=45, ha="right")

ax.set_yticks(np.arange(len(pivot_h.index)))
ax.set_yticklabels(pivot_h.index)

cbar = fig.colorbar(im, ax=ax)
cbar.set_label("Arbeitslosenquote Jüngere (%)")

# dezente Spalten-Trenner, damit man beim "runterlesen" die Spalte nicht verliert
for x in range(len(pivot_h.columns)):
    ax.axvline(x - 0.5, color="white", linewidth=0.3, alpha=0.7)

fig.tight_layout()
save_fig(fig, "02_heatmap_jugendquote.png")

# ============================================================
# 3) HOTSPOTS: 2019 → 2023 (
# ============================================================
YEAR_A = 2019
YEAR_B = 2023
TOP_SHOW = 6
MUST_INCLUDE = ["Nürnberg"]

df_s = df_long[(df_long["variable"] == VAR_YOUTH) & (df_long["jahr"].isin([YEAR_A, YEAR_B]))].copy()
pivot_s = df_s.pivot_table(index="region", columns="jahr", values="value", aggfunc="mean").dropna()
pivot_s["delta"] = pivot_s[YEAR_B] - pivot_s[YEAR_A]

rank_2023 = pivot_s[YEAR_B].sort_values(ascending=False).index.tolist()

selected = []
for r in MUST_INCLUDE + rank_2023:
    if r in pivot_s.index and r not in selected:
        selected.append(r)
    if len(selected) >= TOP_SHOW:
        break

pivot_s = pivot_s.loc[selected].copy()
pivot_s = pivot_s.sort_values(by=YEAR_B, ascending=False)

# Region-Farben (bunt, aber stabil)
cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
color_map = {r: cycle[i % len(cycle)] for i, r in enumerate(pivot_s.index)}

fig, ax = plt.subplots(figsize=(11, 6))

# graue Hintergrundlinien? -> NEIN, weil nur ausgewählte Regionen
# dafür klare bunte Linien
for r in pivot_s.index:
    y1 = float(pivot_s.loc[r, YEAR_A])
    y2 = float(pivot_s.loc[r, YEAR_B])
    lw = 3.5 if r in MUST_INCLUDE else 3.0
    ax.plot([0, 1], [y1, y2], marker="o", linewidth=lw, color=color_map[r])

ax.set_title(f"Jugendarbeitslosigkeit: Hotspots im Vergleich ({YEAR_A} → {YEAR_B})", pad=12)
ax.set_xticks([0, 1], [str(YEAR_A), str(YEAR_B)])
ax.set_ylabel("Arbeitslosenquote Jüngere (%)")

beautify(ax)

# Platz rechts für farbige Liste (kompakt)
ax.set_xlim(-0.05, 1.28)

x0 = 1.02
y0 = 0.90
dy = 0.085
ax.text(x0, y0 + dy, "Gezeigte Regionen", transform=ax.transAxes, fontweight="bold")

for i, r in enumerate(pivot_s.index):
    y = y0 - i * dy
    d = float(pivot_s.loc[r, "delta"])
    col = color_map[r]
    ax.scatter([x0], [y], transform=ax.transAxes, s=95, color=col)
    ax.text(x0 + 0.03, y, f"{r} ({d:+.2f} pp)", transform=ax.transAxes,
            va="center", fontsize=11, color=col)

fig.tight_layout()
save_fig(fig, "03_hotspots_2019_2023.png")

# ============================================================
# 5) DELTA BAR
# ============================================================
df_delta = pivot_s.copy()
df_delta["delta_pp"] = df_delta[YEAR_B] - df_delta[YEAR_A]
df_delta = df_delta.sort_values("delta_pp")

fig, ax = plt.subplots(figsize=(8.4, 5.3))

colors = [COLOR_TOTAL if v < 0 else COLOR_YOUTH for v in df_delta["delta_pp"]]
ax.barh(df_delta.index, df_delta["delta_pp"], color=colors)
ax.axvline(0, color=COLOR_TOTAL, linewidth=1.2)

ax.set_title(f"Veränderung der Jugendarbeitslosigkeit ({YEAR_A} → {YEAR_B}) – ausgewählte Regionen", pad=12)
ax.set_xlabel("Veränderung in Prozentpunkten (pp)")
ax.set_ylabel("")
beautify(ax)

# Achsenbereich + klare Richtungstexte
x_min = float(df_delta["delta_pp"].min())
x_max = float(df_delta["delta_pp"].max())
pad = 0.08 * (x_max - x_min if x_max != x_min else 1.0)
ax.set_xlim(x_min - pad, x_max + pad)

ax.text(0.01, -0.12, "← sinkt (besser)", transform=ax.transAxes,
        ha="left", va="top", color=COLOR_TOTAL)
ax.text(0.99, -0.12, "steigt (schlechter) →", transform=ax.transAxes,
        ha="right", va="top", color=COLOR_YOUTH)

fig.tight_layout()
save_fig(fig, "05_delta_2019_2023.png")

print("\nFertig! Exportiert nach figures/:")
print(" - 01_line_jugend_vs_gesamt.png")
print(" - 02_heatmap_jugendquote.png")
print(" - 03_hotspots_2019_2023.png")
print(" - 04_scatter_2023.png")
print(" - 05_delta_2019_2023.png")
