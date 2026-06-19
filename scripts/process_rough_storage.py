import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = PROJECT_DIR / "data" / "raw"
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

PROCESSED_DATA.mkdir(parents=True, exist_ok=True)
OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

input_path = RAW_DATA / "national_gas_rough_storage_2026.csv"

storage = pd.read_csv(input_path)

storage = storage.rename(columns={
    "Applicable For": "date",
    "Data Item": "data_item",
    "Value": "rough_opening_stock",
    "Generated Time": "generated_time"
})

storage["date"] = pd.to_datetime(storage["date"], dayfirst=True)
storage["generated_time"] = pd.to_datetime(storage["generated_time"], dayfirst=True)
storage["rough_opening_stock"] = pd.to_numeric(
    storage["rough_opening_stock"],
    errors="coerce"
)

# Some National Gas downloads can contain repeated dates.
# Keep the latest published value for each gas day.
storage = (
    storage
    .sort_values(["date", "generated_time"])
    .drop_duplicates(subset=["date"], keep="last")
)

storage = storage[[
    "date",
    "rough_opening_stock"
]].copy()

storage = storage.sort_values("date")

# Convert daily Rough stock into weekly average stock.
weekly_storage = (
    storage
    .set_index("date")
    .resample("W-FRI")
    .mean(numeric_only=True)
    .reset_index()
)

# A simple low-storage pressure variable.
# Higher value means lower Rough stock relative to this sample.
mean_stock = weekly_storage["rough_opening_stock"].mean()
std_stock = weekly_storage["rough_opening_stock"].std()

if std_stock == 0:
    weekly_storage["rough_low_storage_pressure"] = 0
else:
    weekly_storage["rough_low_storage_pressure"] = (
        (mean_stock - weekly_storage["rough_opening_stock"]) / std_stock
    )

output_path = PROCESSED_DATA / "weekly_rough_storage_2026.csv"
weekly_storage.to_csv(output_path, index=False)

print("Processed Rough storage stock data.")
print(f"Saved file to: {output_path}")
print()
print(weekly_storage.head(15))

plt.figure(figsize=(10, 5))
plt.plot(
    weekly_storage["date"],
    weekly_storage["rough_opening_stock"],
    marker="o"
)
plt.title("Weekly Rough Opening Stock - 2026")
plt.xlabel("Date")
plt.ylabel("Opening stock")
plt.xticks(rotation=45)
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "weekly_rough_storage_2026.png"
plt.savefig(chart_path, dpi=150)

print()
print(f"Saved chart to: {chart_path}")
