import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = PROJECT_DIR / "data" / "raw"
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

PROCESSED_DATA.mkdir(parents=True, exist_ok=True)
OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

input_path = RAW_DATA / "national_gas_south_hook_lng_2026.csv"

lng = pd.read_csv(input_path)

lng = lng.rename(columns={
    "Applicable For": "date",
    "Data Item": "data_item",
    "Value": "value",
    "Generated Time": "generated_time",
    "Quality Indicator": "quality_indicator"
})

lng["date"] = pd.to_datetime(lng["date"], dayfirst=True)
lng["generated_time"] = pd.to_datetime(lng["generated_time"], dayfirst=True)
lng["value"] = pd.to_numeric(lng["value"], errors="coerce")

# Keep South Hook D+1 entry energy as the daily LNG send-out proxy.
lng = lng[lng["data_item"] == "System Entry Energy, SouthHook, D+1"].copy()

# Some days have repeated publications. Prefer quality A where available,
# otherwise keep the latest generated value.
quality_rank = {
    "A": 2,
    "L": 1
}

lng["quality_rank"] = lng["quality_indicator"].map(quality_rank).fillna(0)

lng = (
    lng
    .sort_values(["date", "quality_rank", "generated_time"])
    .drop_duplicates(subset=["date"], keep="last")
)

lng = lng[[
    "date",
    "value"
]].rename(columns={
    "value": "south_hook_entry_energy"
})

lng = lng.sort_values("date")

# National Gas values here are large energy values.
# Convert to GWh as a readable scale if the original values are in kWh.
lng["south_hook_entry_energy_gwh"] = lng["south_hook_entry_energy"] / 1_000_000

weekly_lng = (
    lng
    .set_index("date")
    .resample("W-FRI")
    .mean(numeric_only=True)
    .reset_index()
)

# Low LNG pressure: higher when South Hook send-out is below its sample average.
mean_lng = weekly_lng["south_hook_entry_energy_gwh"].mean()
std_lng = weekly_lng["south_hook_entry_energy_gwh"].std()

if std_lng == 0:
    weekly_lng["low_south_hook_lng_pressure"] = 0
else:
    weekly_lng["low_south_hook_lng_pressure"] = (
        mean_lng - weekly_lng["south_hook_entry_energy_gwh"]
    ) / std_lng

output_path = PROCESSED_DATA / "weekly_south_hook_lng_2026.csv"
weekly_lng.to_csv(output_path, index=False)

print("Processed South Hook LNG terminal entry energy.")
print(f"Saved file to: {output_path}")
print()
print(weekly_lng.head(20))

plt.figure(figsize=(10, 5))
plt.plot(
    weekly_lng["date"],
    weekly_lng["south_hook_entry_energy_gwh"],
    marker="o"
)
plt.title("Weekly South Hook LNG Entry Energy - 2026")
plt.xlabel("Date")
plt.ylabel("GWh")
plt.xticks(rotation=45)
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "weekly_south_hook_lng_2026.png"
plt.savefig(chart_path, dpi=150)

print()
print(f"Saved chart to: {chart_path}")
