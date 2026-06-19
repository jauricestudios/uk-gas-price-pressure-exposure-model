import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"

weather_path = PROCESSED_DATA / "weather_weekly_hdd_2026.csv"
wind_path = PROCESSED_DATA / "neso_weekly_wind_demand_2026.csv"

weather = pd.read_csv(weather_path)
wind = pd.read_csv(wind_path)

weather["date"] = pd.to_datetime(weather["date"])
wind["date"] = pd.to_datetime(wind["date"])

# Keep only the weather columns we need
weather = weather[[
    "date",
    "avg_temperature_c",
    "hdd",
    "hdd_dev"
]].copy()

# Keep only the NESO columns we need
wind = wind[[
    "date",
    "ND",
    "TSD",
    "ENGLAND_WALES_DEMAND",
    "EMBEDDED_WIND_GENERATION",
    "EMBEDDED_SOLAR_GENERATION",
    "wind_shortfall"
]].copy()

# Merge the two real drivers by week-ending date
drivers = pd.merge(
    weather,
    wind,
    on="date",
    how="inner"
)

output_path = PROCESSED_DATA / "real_driver_inputs_2026.csv"
drivers.to_csv(output_path, index=False)

print("Built real driver input file.")
print(f"Saved file to: {output_path}")
print()
print(drivers.head(10))
print()
print("Rows:", len(drivers))

