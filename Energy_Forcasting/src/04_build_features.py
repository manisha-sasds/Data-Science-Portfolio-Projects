from pathlib import Path
import pandas as pd

PROCESSED = Path('data/processed')

cons = pd.read_csv(PROCESSED / 'consumption_clean.csv', parse_dates=['timestamp'])
weather = pd.read_csv(PROCESSED / 'weather_clean.csv', parse_dates=['timestamp'])
customers = pd.read_csv(PROCESSED / 'customers_clean.csv', parse_dates=['active_from','active_to'])
calendar = pd.read_csv(PROCESSED / 'calendar_clean.csv', parse_dates=['timestamp','date'])

# 1. Portfolio demand: one row per half-hour
portfolio = cons.groupby('timestamp', as_index=False)['consumption_kwh'].sum()
portfolio = portfolio.rename(columns={'consumption_kwh':'total_consumption_kwh'})

# 2. Average UK-regional weather for each half-hour
weather_portfolio = (weather.groupby('timestamp', as_index=False)
                     .agg(temperature_c=('temperature_c','mean'),
                          wind_speed_mps=('wind_speed_mps','mean'),
                          cloud_cover_pct=('cloud_cover_pct','mean')))

# 3. Calendar fields
cal_cols = ['timestamp','settlement_period','is_weekend','is_bank_holiday']
features = portfolio.merge(calendar[cal_cols], on='timestamp', how='left', validate='one_to_one')
features = features.merge(weather_portfolio, on='timestamp', how='left', validate='one_to_one')

# 4. Number of active customers at each timestamp
# active_to is interpreted as active through that date.
def active_count(ts):
    active = (customers['active_from'] <= ts) & (customers['active_to'].isna() | (customers['active_to'] >= ts.normalize()))
    return int(active.sum())

features['active_customer_count'] = features['timestamp'].apply(active_count)

# 5. Time features
features['hour'] = features['timestamp'].dt.hour
features['minute'] = features['timestamp'].dt.minute
features['day_of_week'] = features['timestamp'].dt.dayofweek
features['month'] = features['timestamp'].dt.month

# 6. Heating degree feature: larger when temperature is below 15.5C
features['heating_degree'] = (15.5 - features['temperature_c']).clip(lower=0)

# 7. Lag features. Data MUST be sorted before shift.
features = features.sort_values('timestamp').reset_index(drop=True)
features['lag_1'] = features['total_consumption_kwh'].shift(1)
features['lag_48'] = features['total_consumption_kwh'].shift(48)
features['lag_336'] = features['total_consumption_kwh'].shift(336)

# Rolling mean uses shift(1) so current target is not leaked.
features['rolling_48_mean'] = features['total_consumption_kwh'].shift(1).rolling(48).mean()

features.to_csv(PROCESSED / 'model_features.csv', index=False)
print('Feature table shape:', features.shape)
print(features.head())
print('\nSaved: data/processed/model_features.csv')
