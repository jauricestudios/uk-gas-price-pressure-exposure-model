import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_DIR / "data" / "processed" / "daily_global_gas_prices_gbp_2021_2026.csv"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH, parse_dates=["date"])
df["year"] = df["date"].dt.year

spread_cols = [
    "jkm_ttf_spread_gbp_per_mwh",
    "jkm_nbp_spread_gbp_per_mwh"
]

summary = df.groupby("year")[spread_cols].agg(["mean", "median", "min", "max", "std"])
summary.columns = ["_".join(col).strip() for col in summary.columns]
summary = summary.reset_index()

overall = df[spread_cols].agg(["mean", "median", "min", "max", "std"]).T
overall = overall.reset_index().rename(columns={"index": "spread"})
overall["year"] = "2021-2026"

output_path = OUTPUT_TABLES / "global_gas_spread_summary_2021_2026.csv"
summary.to_csv(output_path, index=False)

overall_path = OUTPUT_TABLES / "global_gas_spread_overall_summary_2021_2026.csv"
overall.to_csv(overall_path, index=False)

print("Annual global gas spread summary")
print(summary)
print()
print("Overall summary")
print(overall)
print()
print(f"Saved annual table to: {output_path}")
print(f"Saved overall table to: {overall_path}")
