"""Einlesung der Daten"""
#ChatGPT:
#Du bist ein Coding-Assistent für ein universitäres Datenvisualisierungsprojekt.
#Erstelle in Python ein vollständig auskommentiertes Skript zur Datenaufbereitung,
#das eine deutsche INKAR CSV Datei zur Arbeitslosigkeit einliest. Die erste Zeile der
#Datei enthält die Jahresangaben der Wertspalten. Entferne automatisch erzeugte
#„Unnamed“-Spalten und verarbeite die Daten. Die Daten sollen in ein übersichtliches Long-/Tidy-Format überführt werden, das
#für weitere Auswertungen und Visualisierungen geeignet ist. Ergänze einfache
#Plausibilitäts- bzw. Qualitätschecks per print-Ausgaben und speichere den
#bereinigten Datensatz als CSV-Datei. Gib ausschließlich den lauffähigen
#Python-Code aus. Gib ausschließlich den vollständigen, direkt lauffähigen Python-Code aus.


import os
import pandas as pd
import numpy as np

# ------------------------------------------------------------
# 0) Settings / Pfade
# ------------------------------------------------------------

# Projektordner: .../Datenvisualisierung
# __file__ ist die aktuelle Datei (phase1_datenaufbereitung.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "Arbeitslosigkeit_inkar_Datenvis.csv")
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")
os.makedirs(CLEAN_DIR, exist_ok=True)

OUT_PATH = os.path.join(CLEAN_DIR, "clean_long.csv")


print("Projektordner:", BASE_DIR)
print("CSV-Pfad:", RAW_PATH)

# ------------------------------------------------------------
# 1) CSV einlesen
# ------------------------------------------------------------
# sep=";" -> deutsche CSVs nutzen oft Semikolon
# decimal="," -> deutsche Dezimalzahlen (1,23)
df = pd.read_csv(RAW_PATH, sep=";", decimal=",")

print("\nErste 5 Zeilen (Rohdaten):")
print(df.head())

print("\nSpaltenanzahl:", df.shape[1], "| Zeilenanzahl:", df.shape[0])

# ------------------------------------------------------------
# 2) Die erste Zeile enthält oft die Jahre (bei dir: Zeile 0)
#    Diese Zeile speichern wir, bevor wir sie entfernen!
# ------------------------------------------------------------
year_row = df.iloc[0].copy()

# ------------------------------------------------------------
# 3) "Unnamed" Spalten entfernen (z.B. "Unnamed: 2")
#    Diese Spalten sind meistens leer und stören nur.
# ------------------------------------------------------------
mask_unnamed = df.columns.str.contains(r"^Unnamed")
df = df.loc[:, ~mask_unnamed].copy()

# year_row muss die gleichen Spalten behalten wie df
year_row = year_row.loc[df.columns]

print("\nSpalten nach Entfernen von 'Unnamed':", df.shape[1])

# ------------------------------------------------------------
# 4) Jahre-Zeile entfernen
#    Ab Zeile 1 kommen die echten Regionen-Daten
# ------------------------------------------------------------
df = df.iloc[1:].copy()

# ------------------------------------------------------------
# 5) Kennziffer sauber machen (Zahl / Integer)
# ------------------------------------------------------------
if "Kennziffer" in df.columns:
    df["Kennziffer"] = pd.to_numeric(df["Kennziffer"], errors="coerce").astype("Int64")

# ------------------------------------------------------------
# 6) Welche Spalten enthalten Werte über die Jahre?
#    Alles außer Kennziffer und Raumeinheit sind "Wertspalten"
# ------------------------------------------------------------
id_cols = ["Kennziffer", "Raumeinheit"]
value_cols = [c for c in df.columns if c not in id_cols]

# ------------------------------------------------------------
# 7) Mapping: Spaltenname -> Jahr
#    In year_row steht pro Spalte das Jahr (z.B. 2010, 2011, ...)
#    Manche Spalten können NaN haben -> die ignorieren wir.
# ------------------------------------------------------------
col_to_year = {}
for c in value_cols:
    y = pd.to_numeric(year_row[c], errors="coerce")
    if pd.notna(y):
        col_to_year[c] = int(y)

# Nur Spalten nutzen, die wirklich ein Jahr haben:
value_cols_valid = [c for c in value_cols if c in col_to_year]

print("\nAnzahl Wertspalten:", len(value_cols))
print("Anzahl Wertspalten mit Jahr:", len(value_cols_valid))

# ------------------------------------------------------------
# 8) Von "wide" zu "long" (tidy) umformen
#    -> eine Zeile = (Region, Variable, Jahr, Wert)
# ------------------------------------------------------------
df_long = df.melt(
    id_vars=id_cols,
    value_vars=value_cols_valid,
    var_name="variable_raw",
    value_name="value"
)

# Jahr hinzufügen
df_long["jahr"] = df_long["variable_raw"].map(col_to_year)

# Werte numerisch
df_long["value"] = pd.to_numeric(df_long["value"], errors="coerce")

# ------------------------------------------------------------
# 9) Variable sauber machen:
#    "Arbeitslosenquote.12" -> "Arbeitslosenquote"
# ------------------------------------------------------------
df_long["variable"] = df_long["variable_raw"].str.replace(r"\.\d+$", "", regex=True)

# Optional: schöner umbenennen
df_long = df_long.rename(columns={
    "Raumeinheit": "region"
})

# Reihenfolge der Spalten
df_long = df_long[["Kennziffer", "region", "jahr", "variable", "value", "variable_raw"]]

# ------------------------------------------------------------
# 10) Kurzer Qualitätscheck
# ------------------------------------------------------------
print("\nTIDY-DATEN Vorschau:")
print(df_long.head(10))

print("\nJahr min/max:", df_long["jahr"].min(), df_long["jahr"].max())
print("Zeilen/Spalten:", df_long.shape)

print("\nTop 15 Variablen (wie oft vorhanden):")
print(df_long["variable"].value_counts().head(15))

# ------------------------------------------------------------
# 11) Speichern
# ------------------------------------------------------------
df_long.to_csv(OUT_PATH, index=False)
print("\n Gespeichert:", OUT_PATH)


