import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = PROJECT_DIR / "data" / "raw"
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

PROCESSED_DATA.mkdir(parents=True, exist_ok=True)
OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)


def clean_storage_file(path):
    df = pd.read_csv(path)

    df = df.rename(columns={
        "Applicable For": "date",
        "Data Item": "data_item",
        "Value": "value",
        "Generated Time": "generated_time"
    })

    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df["generated_time"] = pd.to_datetime(df["generated_time"], dayfirst=True)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Keep the latest published value for each gas day and data item.
    df = (
        df
        .sort_values(["date", "data_item", "generated_time"])
        .drop_duplicates(subset=["date", "data_item"], keep="last")
    )

    return df[["date", "data_item", "value"]]


long_path = RAW_DATA / "national_gas_long_range_storage_2026.csv"
medium_short_path = RAW_DATA / "national_gas_medium_short_storage_2026.csv"

long_storage = clean_storage_file(long_path)
medium_short_storage = clean_storage_file(medium_short_path)

storage = pd.concat(
    [long_storage, medium_short_storage],
    ignore_index=True
)

storage_wide = (
    storage
    .pivot_table(
        index="date",
        columns="data_item",
        values="value",
        aggfunc="mean"
    )
    .reset_index()
)

storage_wide = storage_wide.rename(columns={
    "Storage, Long Range, Stock Levels": "long_range_storage",
    "Storage, Medium Range, Stock Levels": "medium_range_storage",
    "Storage, Short Range, Stock Levels": "short_range_storage"
})

for col in ["long_range_storage", "medium_range_storage", "short_range_storage"]:
    if col not in storage_wide.columns:
        storage_wide[col] = 0

storage_wide = storage_wide.sort_values("date")

storage_wide["total_storage_stock"] = (
    storage_wide["long_range_storage"].fillna(0)
    + storage_wide["medium_range_storage"].fillna(0)
    + storage_wide["short_range_storage"].fillna(0)
)

weekly_storage = (
    storage_wide
    .set_index("date")
    .resample("W-FRI")
    .mean(numeric_only=True)
    .reset_index()
)

# Higher pressure means storage is lower than its own sample average.
mean_storage = weekly_storage["total_storage_stock"].mean()
std_storage = weekly_storage["total_storage_stock"].std()

if std_storage == 0:
    weekly_storage["low_storage_pressure"] = 0
else:
    weekly_storage["low_storage_pressure"] = (
        mean_storage - weekly_storage["total_storage_stock"]
    ) / std_storage

output_path = PROCESSED_DATA / "weekly_storage_stock_2026.csv"
weekly_storage.to_csv(output_path, index=False)

print("Processed National Gas storage stock levels.")
print(f"Saved file to: {output_path}")
print()
print(weekly_storage.head(15))

plt.figure(figsize=(10, 5))
plt.plot(
    weekly_storage["date"],
    weekly_storage["total_storage_stock"],
    marker="o"
)
plt.title("Weekly UK Storage Stock Levels - 2026")
plt.xlabel("Date")
plt.ylabel("Storage stock level")
plt.xticks(rotation=45)
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "weekly_storage_stock_2026.png"
plt.savefig(chart_path, dpi=150)

print()
print(f"Saved chart to: {chart_path}")
