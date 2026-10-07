from pathlib import Path
import pandas as pd

RAW = Path('data/raw')
files = ['half_hourly_consumption.csv','weather.csv','customer_master.csv','calendar.csv','future_weather_forecast.csv']

for file in files:
    df = pd.read_csv(RAW / file)
    print('\n' + '='*70)
    print(file)
    print('='*70)
    print('Shape:', df.shape)
    print('\nData types:\n', df.dtypes)
    print('\nMissing values:\n', df.isna().sum())
    print('\nDuplicate rows:', df.duplicated().sum())
    print('\nFirst 5 rows:\n', df.head())
