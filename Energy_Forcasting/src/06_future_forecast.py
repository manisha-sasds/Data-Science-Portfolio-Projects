from pathlib import Path
import pandas as pd
import joblib

PROCESSED = Path('data/processed')
OUTPUT = Path('output')
OUTPUT.mkdir(exist_ok=True)

bundle = joblib.load('models/portfolio_model.joblib')
model = bundle['model']
feature_cols = bundle['feature_cols']

history = pd.read_csv(PROCESSED / 'model_features.csv', parse_dates=['timestamp'])
future_weather = pd.read_csv(PROCESSED / 'future_weather_clean.csv', parse_dates=['timestamp'])
customers = pd.read_csv(PROCESSED / 'customers_clean.csv', parse_dates=['active_from','active_to'])

# Average future weather across regions to match the portfolio model.
future = (future_weather.groupby('timestamp', as_index=False)
          .agg(temperature_c=('forecast_temperature_c','mean'),
               wind_speed_mps=('forecast_wind_speed_mps','mean')))

# Historical model had cloud cover, but future file does not.
# Use historical average cloud cover as a simple explicit assumption.
future['cloud_cover_pct'] = history['cloud_cover_pct'].mean()

future['settlement_period'] = future['timestamp'].dt.hour * 2 + future['timestamp'].dt.minute // 30 + 1
future['is_weekend'] = future['timestamp'].dt.dayofweek >= 5
future['is_bank_holiday'] = False  # Simple assumption for this practice forecast.
future['hour'] = future['timestamp'].dt.hour
future['minute'] = future['timestamp'].dt.minute
future['day_of_week'] = future['timestamp'].dt.dayofweek
future['month'] = future['timestamp'].dt.month
future['heating_degree'] = (15.5 - future['temperature_c']).clip(lower=0)

def active_count(ts):
    active = (customers['active_from'] <= ts) & (customers['active_to'].isna() | (customers['active_to'] >= ts.normalize()))
    return int(active.sum())

future['active_customer_count'] = future['timestamp'].apply(active_count)

# We forecast one half-hour at a time.
# Each new prediction is appended to history and becomes available for later lags.
series = history[['timestamp','total_consumption_kwh']].dropna().copy()
series = series.sort_values('timestamp').set_index('timestamp')['total_consumption_kwh'].to_dict()

predictions = []
for i, row in future.sort_values('timestamp').iterrows():
    ts = row['timestamp']

    lag1_time = ts - pd.Timedelta(minutes=30)
    lag48_time = ts - pd.Timedelta(days=1)
    lag336_time = ts - pd.Timedelta(days=7)

    lag_1 = series.get(lag1_time)
    lag_48 = series.get(lag48_time)
    lag_336 = series.get(lag336_time)

    previous_48_times = [ts - pd.Timedelta(minutes=30*j) for j in range(1,49)]
    previous_48_values = [series.get(t) for t in previous_48_times]
    previous_48_values = [x for x in previous_48_values if x is not None]
    rolling_48_mean = sum(previous_48_values) / len(previous_48_values)

    X = pd.DataFrame([{
        'settlement_period': row['settlement_period'],
        'is_weekend': row['is_weekend'],
        'is_bank_holiday': row['is_bank_holiday'],
        'temperature_c': row['temperature_c'],
        'wind_speed_mps': row['wind_speed_mps'],
        'cloud_cover_pct': row['cloud_cover_pct'],
        'active_customer_count': row['active_customer_count'],
        'hour': row['hour'],
        'minute': row['minute'],
        'day_of_week': row['day_of_week'],
        'month': row['month'],
        'heating_degree': row['heating_degree'],
        'lag_1': lag_1,
        'lag_48': lag_48,
        'lag_336': lag_336,
        'rolling_48_mean': rolling_48_mean
    }])[feature_cols]

    prediction = float(model.predict(X)[0])
    prediction = max(prediction, 0)
    series[ts] = prediction
    predictions.append(prediction)

future = future.sort_values('timestamp').copy()
future['forecast_consumption_kwh'] = predictions
future[['timestamp','forecast_consumption_kwh','temperature_c','active_customer_count']].to_csv(
    OUTPUT / '14_day_portfolio_forecast.csv', index=False
)

print(future[['timestamp','forecast_consumption_kwh']].head())
print('\nForecast saved: output/14_day_portfolio_forecast.csv')
