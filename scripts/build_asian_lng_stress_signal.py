from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# Asian LNG stress signal
#
# Purpose:
# Build a clean JKM-vs-TTF signal.
#
# Logic:
# If JKM trades above TTF, Asian LNG demand may be pulling
# flexible LNG cargoes away from Europe. That can raise the
# replacement cost Europe/UK must pay for LNG.
# ---------------------------------------------------------

SEARCH_ROOTS = [Path("data/raw"), Path("data/processed"), Path(".")]

def find_file(patterns):
    candidates = []
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for f in root.rglob("*.csv"):
            name = f.name.lower()
            path = str(f).lower()

            # Skip build/venv junk
            if "_build" in path or ".venv" in path or "site-packages" in path:
                continue

            if all(p.lower() in name for p in patterns):
                candidates.append(f)

    if not candidates:
        raise FileNotFoundError(f"Could not find CSV matching: {patterns}")

    candidates = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def read_market_csv(path):
    df = pd.read_csv(path)

    # Identify date column
    date_col = None
    for col in df.columns:
        c = col.lower()
        if c in ["date", "time"] or "date" in c or "time" in c:
            date_col = col
            break

    if date_col is None:
        raise ValueError(f"No date/time column found in {path}. Columns: {list(df.columns)}")

    # Identify price column
    price_col = None
    preferred = ["last", "close", "price", "settle"]
    for target in preferred:
        for col in df.columns:
            if col.lower().strip() == target:
                price_col = col
                break
        if price_col:
            break

    if price_col is None:
        for col in df.columns:
            c = col.lower()
            if "last" in c or "close" in c or "price" in c or "settle" in c:
                price_col = col
                break

    if price_col is None:
        raise ValueError(f"No price column found in {path}. Columns: {list(df.columns)}")

    out = df[[date_col, price_col]].copy()
    out.columns = ["Date", "Price"]

    out["Date"] = pd.to_datetime(out["Date"], errors="coerce")
    out["Price"] = (
        out["Price"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
    )
    out["Price"] = pd.to_numeric(out["Price"], errors="coerce")

    out = out.dropna(subset=["Date", "Price"])
    out = out.sort_values("Date")
    out = out.drop_duplicates("Date", keep="last")

    return out


print("Finding raw market files...")

# These patterns match the files you downloaded earlier
jkm_file = find_file(["jkm"])
ttf_file = find_file(["tgn"])      # Barchart TTF nearby / TGN file
nbp_file = find_file(["nfn"])      # Barchart NBP nearby / NFN file
gbpusd_file = find_file(["gbpusd"])
eurgbp_file = find_file(["eurgbp"])

print(f"JKM file:    {jkm_file}")
print(f"TTF file:    {ttf_file}")
print(f"NBP file:    {nbp_file}")
print(f"GBPUSD file: {gbpusd_file}")
print(f"EURGBP file: {eurgbp_file}")

jkm = read_market_csv(jkm_file).rename(columns={"Price": "JKM_USD_MMBtu"})
ttf = read_market_csv(ttf_file).rename(columns={"Price": "TTF_EUR_MWh"})
nbp = read_market_csv(nbp_file).rename(columns={"Price": "NBP_pence_therm"})
gbpusd = read_market_csv(gbpusd_file).rename(columns={"Price": "GBPUSD"})
eurgbp = read_market_csv(eurgbp_file).rename(columns={"Price": "EURGBP"})

# Merge daily data
df = jkm.merge(ttf, on="Date", how="outer")
df = df.merge(nbp, on="Date", how="outer")
df = df.merge(gbpusd, on="Date", how="outer")
df = df.merge(eurgbp, on="Date", how="outer")

df = df.sort_values("Date")

# FX can be forward-filled across non-trading days
df[["GBPUSD", "EURGBP"]] = df[["GBPUSD", "EURGBP"]].ffill()

# Keep rows where benchmark prices exist
df = df.dropna(subset=["JKM_USD_MMBtu", "TTF_EUR_MWh", "NBP_pence_therm", "GBPUSD", "EURGBP"]).copy()

# Unit conversions
# JKM: USD/MMBtu -> GBP/MWh
# 1 MWh = 3.412141633 MMBtu
df["JKM_GBP_MWh"] = df["JKM_USD_MMBtu"] * 3.412141633 / df["GBPUSD"]

# TTF: EUR/MWh -> GBP/MWh
df["TTF_GBP_MWh"] = df["TTF_EUR_MWh"] * df["EURGBP"]

# NBP: pence/therm -> GBP/MWh
# 1 therm = 0.0293071 MWh
df["NBP_GBP_MWh"] = (df["NBP_pence_therm"] / 100) / 0.0293071

# Spreads
df["JKM_TTF_Spread_GBP_MWh"] = df["JKM_GBP_MWh"] - df["TTF_GBP_MWh"]
df["JKM_NBP_Spread_GBP_MWh"] = df["JKM_GBP_MWh"] - df["NBP_GBP_MWh"]
df["JKM_TTF_Premium_Percent"] = df["JKM_TTF_Spread_GBP_MWh"] / df["TTF_GBP_MWh"]

# Stress thresholds from actual JKM-TTF spread distribution
q75 = df["JKM_TTF_Spread_GBP_MWh"].quantile(0.75)
q90 = df["JKM_TTF_Spread_GBP_MWh"].quantile(0.90)

def stress_level(x):
    if x >= q90:
        return "Extreme"
    if x >= q75:
        return "High"
    if x > 0:
        return "Medium"
    return "Low"

df["Asian_LNG_Stress_Level"] = df["JKM_TTF_Spread_GBP_MWh"].apply(stress_level)
df["Asian_LNG_Stress_Flag"] = df["Asian_LNG_Stress_Level"].isin(["High", "Extreme"])

# Export clean table
out = df[[
    "Date",
    "JKM_GBP_MWh",
    "TTF_GBP_MWh",
    "NBP_GBP_MWh",
    "JKM_TTF_Spread_GBP_MWh",
    "JKM_NBP_Spread_GBP_MWh",
    "JKM_TTF_Premium_Percent",
    "Asian_LNG_Stress_Level",
    "Asian_LNG_Stress_Flag"
]].copy()

Path("outputs/tables").mkdir(parents=True, exist_ok=True)
Path("outputs/charts").mkdir(parents=True, exist_ok=True)

table_out = Path("outputs/tables/asian_lng_stress_signal.csv")
out.to_csv(table_out, index=False)

print("\nLatest Asian LNG stress signal:")
print(out.tail(8).round(2).to_string(index=False))

print(f"\n75th percentile spread: {q75:.2f} GBP/MWh")
print(f"90th percentile spread: {q90:.2f} GBP/MWh")
print(f"Saved table: {table_out}")

# Chart
chart_out = Path("outputs/charts/asian_lng_stress_jkm_ttf_spread.png")

plt.figure(figsize=(10, 5))
plt.plot(out["Date"], out["JKM_TTF_Spread_GBP_MWh"], linewidth=1.6)
plt.axhline(q75, linestyle="--", linewidth=1)
plt.axhline(q90, linestyle="--", linewidth=1)
plt.axhline(0, linewidth=1)
plt.title("Asian LNG Stress Signal: JKM minus TTF")
plt.xlabel("Date")
plt.ylabel("Spread, GBP/MWh")
plt.tight_layout()
plt.savefig(chart_out, dpi=200)
plt.close()

print(f"Saved chart: {chart_out}")
