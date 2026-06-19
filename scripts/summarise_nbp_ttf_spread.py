import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_DIR / "data" / "processed" / "daily_barchart_nbp_ttf_nearby_with_fx_2021_2026.csv"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH, parse_dates=["date"])

df["year"] = df["date"].dt.year

summary = df.groupby("year")["nbp_ttf_spread_gbp_per_mwh"].agg(
    mean_spread="mean",
    median_spread="median",
    min_spread="min",
    max_spread="max",
    std_spread="std"
).reset_index()

overall = pd.DataFrame({
    "year": ["2021-2026"],
    "mean_spread": [df["nbp_ttf_spread_gbp_per_mwh"].mean()],
    "median_spread": [df["nbp_ttf_spread_gbp_per_mwh"].median()],
    "min_spread": [df["nbp_ttf_spread_gbp_per_mwh"].min()],
    "max_spread": [df["nbp_ttf_spread_gbp_per_mwh"].max()],
    "std_spread": [df["nbp_ttf_spread_gbp_per_mwh"].std()],
})

summary = pd.concat([summary, overall], ignore_index=True)

output_path = OUTPUT_TABLES / "nbp_ttf_spread_summary_2021_2026.csv"
summary.to_csv(output_path, index=False)

print("NBP-TTF spread summary, £/MWh")
print(summary)
print()
print(f"Saved table to: {output_path}")

largest_discount = df.loc[df["nbp_ttf_spread_gbp_per_mwh"].idxmin()]
largest_premium = df.loc[df["nbp_ttf_spread_gbp_per_mwh"].idxmax()]

print()
print("Largest NBP discount to TTF:")
print(largest_discount[["date", "nbp_ttf_spread_gbp_per_mwh", "nbp_price_gbp_per_mwh", "ttf_price_gbp_per_mwh"]])

print()
print("Largest NBP premium to TTF:")
print(largest_premium[["date", "nbp_ttf_spread_gbp_per_mwh", "nbp_price_gbp_per_mwh", "ttf_price_gbp_per_mwh"]])
