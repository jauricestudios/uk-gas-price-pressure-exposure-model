from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path.cwd()

JKM_FILE = ROOT / "data/raw/barchart_jkm_lng_daily_nearby_2021_2026.csv"
TTF_FILE = ROOT / "data/raw/barchart_ttf_daily_nearby_2021_2026.csv"
NBP_FILE = ROOT / "data/raw/barchart_nbp_daily_nearby_2021_2026.csv"
GBPUSD_FILE = ROOT / "data/raw/barchart_gbpusd_daily_2021_2026.csv"
EURGBP_FILE = ROOT / "data/raw/barchart_eurgbp_daily_2021_2026.csv"

for f in [JKM_FILE, TTF_FILE, NBP_FILE, GBPUSD_FILE, EURGBP_FILE]:
    if not f.exists():
        raise FileNotFoundError(f"Missing file: {f}")

def read_barchart_file(path, value_name):
    df = pd.read_csv(path)

    print(f"\nReading: {path}")
    print("Columns:", list(df.columns))

    date_col = None
    for col in df.columns:
        if col.lower().strip() in ["date", "time"]:
            date_col = col
            break

    if date_col is None:
        raise ValueError(f"No date column found in {path}")

    price_col = None
    for preferred in ["Latest", "Last", "Close", "Price", "Settle"]:
        if preferred in df.columns:
            price_col = preferred
            break

    if price_col is None:
        for col in df.columns:
            c = col.lower()
            if "latest" in c or "last" in c or "close" in c or "price" in c or "settle" in c:
                price_col = col
                break

    if price_col is None:
        raise ValueError(f"No price column found in {path}")

    out = df[[date_col, price_col]].copy()
    out.columns = ["Date", value_name]

    out["Date"] = pd.to_datetime(out["Date"], errors="coerce")
    out[value_name] = (
        out[value_name]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
    )
    out[value_name] = pd.to_numeric(out[value_name], errors="coerce")

    out = out.dropna(subset=["Date", value_name])
    out = out.sort_values("Date")
    out = out.drop_duplicates("Date", keep="last")

    return out

jkm = read_barchart_file(JKM_FILE, "JKM_USD_MMBtu")
ttf = read_barchart_file(TTF_FILE, "TTF_EUR_MWh")
nbp = read_barchart_file(NBP_FILE, "NBP_pence_therm")
gbpusd = read_barchart_file(GBPUSD_FILE, "GBPUSD")
eurgbp = read_barchart_file(EURGBP_FILE, "EURGBP")

df = jkm.merge(ttf, on="Date", how="outer")
df = df.merge(nbp, on="Date", how="outer")
df = df.merge(gbpusd, on="Date", how="outer")
df = df.merge(eurgbp, on="Date", how="outer")

df = df.sort_values("Date")

# Forward-fill because FX and futures files may have different holiday calendars.
cols = ["JKM_USD_MMBtu", "TTF_EUR_MWh", "NBP_pence_therm", "GBPUSD", "EURGBP"]
df[cols] = df[cols].ffill()

df = df.dropna(subset=cols).copy()

# Unit conversions
# JKM: USD/MMBtu -> GBP/MWh
# 1 MWh = 3.412141633 MMBtu
df["JKM_GBP_MWh"] = df["JKM_USD_MMBtu"] * 3.412141633 / df["GBPUSD"]

# TTF: EUR/MWh -> GBP/MWh
df["TTF_GBP_MWh"] = df["TTF_EUR_MWh"] * df["EURGBP"]

# NBP: pence/therm -> GBP/MWh
# 1 therm = 0.0293071 MWh
df["NBP_GBP_MWh"] = (df["NBP_pence_therm"] / 100) / 0.0293071

df["JKM_TTF_Spread_GBP_MWh"] = df["JKM_GBP_MWh"] - df["TTF_GBP_MWh"]
df["JKM_NBP_Spread_GBP_MWh"] = df["JKM_GBP_MWh"] - df["NBP_GBP_MWh"]
df["JKM_TTF_Premium_Percent"] = df["JKM_TTF_Spread_GBP_MWh"] / df["TTF_GBP_MWh"]

positive_spreads = df.loc[df["JKM_TTF_Spread_GBP_MWh"] > 0, "JKM_TTF_Spread_GBP_MWh"]

if len(positive_spreads) > 10:
    q75 = positive_spreads.quantile(0.75)
    q90 = positive_spreads.quantile(0.90)
else:
    q75 = df["JKM_TTF_Spread_GBP_MWh"].quantile(0.75)
    q90 = df["JKM_TTF_Spread_GBP_MWh"].quantile(0.90)

def stress_level(x):
    if x <= 0:
        return "Low"
    if x >= q90:
        return "Extreme"
    if x >= q75:
        return "High"
    return "Medium"

df["Asian_LNG_Stress_Level"] = df["JKM_TTF_Spread_GBP_MWh"].apply(stress_level)
df["Asian_LNG_Stress_Flag"] = df["Asian_LNG_Stress_Level"].isin(["High", "Extreme"])

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

table_out = ROOT / "outputs/tables/asian_lng_stress_signal.csv"
out.to_csv(table_out, index=False)

print("\nLatest Asian LNG stress signal:")
print(out.tail(10).round(2).to_string(index=False))

print(f"\n75th percentile positive spread: {q75:.2f} GBP/MWh")
print(f"90th percentile positive spread: {q90:.2f} GBP/MWh")
print(f"Saved table: {table_out}")

chart_out = ROOT / "outputs/charts/asian_lng_stress_jkm_ttf_spread.png"

plt.figure(figsize=(10, 5))
plt.plot(out["Date"], out["JKM_TTF_Spread_GBP_MWh"], linewidth=1.5)
plt.axhline(0, linewidth=1)
plt.axhline(q75, linestyle="--", linewidth=1)
plt.axhline(q90, linestyle="--", linewidth=1)
plt.title("Asian LNG Stress Signal: JKM minus TTF")
plt.xlabel("Date")
plt.ylabel("Spread, GBP/MWh")
plt.tight_layout()
plt.savefig(chart_out, dpi=200)
plt.close()

print(f"Saved chart: {chart_out}")
