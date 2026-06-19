import pandas as pd
import numpy as np
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA = PROJECT_DIR / "data" / "raw"
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"

PROCESSED_DATA.mkdir(parents=True, exist_ok=True)


def z_score(series):
    mean = series.mean()
    std = series.std()

    if std == 0:
        return series * 0

    return (series - mean) / std


input_path = RAW_DATA / "gas_market_template.csv"
df = pd.read_csv(input_path)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

# Price returns. These measure weekly percentage-style movement.
df["nbp_return"] = np.log(df["nbp_price"]).diff()
df["ttf_return"] = np.log(df["ttf_price"]).diff()
df["nbp_lag_return"] = df["nbp_return"].shift(1)

# For now, because this is only a small template, we use sample averages as the normal level.
# Later, with real multi-year data, this will become same-week seasonal averages.
df["storage_dev"] = df["storage_level"] - df["storage_level"].mean()
df["hdd_dev"] = df["hdd"] - df["hdd"].mean()
df["lng_dev"] = df["lng_sendout"] - df["lng_sendout"].mean()

# Wind shortfall is defined so that weak wind increases the tightness signal.
df["wind_shortfall"] = df["wind_generation"].mean() - df["wind_generation"]

df["hdd_z"] = z_score(df["hdd_dev"])
df["storage_z"] = z_score(df["storage_dev"])
df["lng_z"] = z_score(df["lng_dev"])
df["wind_z"] = z_score(df["wind_shortfall"])

df["gti"] = (
    df["hdd_z"]
    - df["storage_z"]
    - df["lng_z"]
    + df["wind_z"]
)

output_path = PROCESSED_DATA / "gas_market_model_ready.csv"
df.to_csv(output_path, index=False)

print("Processed gas market template data.")
print(f"Saved model-ready file to: {output_path}")
print()
print(df[[
    "date",
    "nbp_price",
    "ttf_price",
    "storage_dev",
    "hdd_dev",
    "lng_dev",
    "wind_shortfall",
    "gti"
]])

