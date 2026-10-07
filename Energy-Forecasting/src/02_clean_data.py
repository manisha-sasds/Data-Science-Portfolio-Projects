from pathlib import Path
import pandas as pd

RAW = Path('data/raw')
PROCESSED = Path('data/processed')
PROCESSED.mkdir(parents=True, exist_ok=True)

cons = pd.read_csv(RAW / 'half_hourly_consumption.csv')
weather = pd.read_csv(RAW / 'weather.csv')
customers = pd.read_csv(RAW / 'customer_master.csv')
calendar = pd.read_csv(RAW / 'calendar.csv')
future_weather = pd.read_csv(RAW / 'future_weather_forecast.csv')

# Convert dates
cons['timestamp'] = pd.to_datetime(cons['timestamp'], errors='coerce')
weather['timestamp'] = pd.to_datetime(weather['timestamp'], errors='coerce')
calendar['timestamp'] = pd.to_datetime(calendar['timestamp'], errors='coerce')
calendar['date'] = pd.to_datetime(calendar['date'], errors='coerce')
future_weather['timestamp'] = pd.to_datetime(future_weather['timestamp'], errors='coerce')
customers['active_from'] = pd.to_datetime(customers['active_from'], errors='coerce')
customers['active_to'] = pd.to_datetime(customers['active_to'], errors='coerce')

# Remove exact duplicate meter rows
# Count rows before
before = len(cons)
print('Consumption duplicates removed:', cons.duplicated().sum())
cons = cons.drop_duplicates().copy()
after = len(cons)
print("Rows before:", before)
print("Rows after:", after)
print("Rows deleted:", before - after)


# Keep sensible target values. Negative demand is treated as bad data here.
print('Negative consumption rows removed:', (cons['consumption_kwh'] < 0).sum())
cons = cons[cons['consumption_kwh'] >= 0].copy()

# Weather: sort within region and interpolate temperature.
weather = weather.sort_values(['region', 'timestamp']).copy()
weather['temperature_c'] = weather.groupby('region')['temperature_c'].transform(
    lambda s: s.interpolate(limit_direction='both')
)

# Clean text
cons['customer_id'] = cons['customer_id'].str.strip()
cons['reading_type'] = cons['reading_type'].str.strip().str.upper()
customers['customer_id'] = customers['customer_id'].str.strip()
customers['segment'] = customers['segment'].str.strip()
customers['region'] = customers['region'].str.strip()
weather['region'] = weather['region'].str.strip()
future_weather['region'] = future_weather['region'].str.strip()

# Sort
cons = cons.sort_values(['customer_id', 'timestamp'])
weather = weather.sort_values(['region', 'timestamp'])
calendar = calendar.sort_values('timestamp')
future_weather = future_weather.sort_values(['region', 'timestamp'])

# Save
cons.to_csv(PROCESSED / 'consumption_clean.csv', index=False)
weather.to_csv(PROCESSED / 'weather_clean.csv', index=False)
customers.to_csv(PROCESSED / 'customers_clean.csv', index=False)
calendar.to_csv(PROCESSED / 'calendar_clean.csv', index=False)
future_weather.to_csv(PROCESSED / 'future_weather_clean.csv', index=False)

print('\nCleaned files saved in data/processed/')
