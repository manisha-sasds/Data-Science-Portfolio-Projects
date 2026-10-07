from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

PROCESSED = Path('data/processed')
MODELS = Path('models')
FIGURES = Path('reports/figures')
MODELS.mkdir(exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(PROCESSED / 'model_features.csv', parse_dates=['timestamp'])

feature_cols = [
    'settlement_period','is_weekend','is_bank_holiday',
    'temperature_c','wind_speed_mps','cloud_cover_pct',
    'active_customer_count','hour','minute','day_of_week','month',
    'heating_degree','lag_1','lag_48','lag_336','rolling_48_mean'
]
target = 'total_consumption_kwh'

# Remove early rows where lag 336 does not yet exist.
df = df.dropna(subset=feature_cols + [target]).copy()

# Chronological split: first 70% train, next 15% validation, last 15% test.
n = len(df)
train_end = int(n * 0.70)
valid_end = int(n * 0.85)

train = df.iloc[:train_end].copy()
valid = df.iloc[train_end:valid_end].copy()
test = df.iloc[valid_end:].copy()

print('Train:', train['timestamp'].min(), 'to', train['timestamp'].max(), len(train))
print('Validation:', valid['timestamp'].min(), 'to', valid['timestamp'].max(), len(valid))
print('Test:', test['timestamp'].min(), 'to', test['timestamp'].max(), len(test))

X_train = train[feature_cols]
y_train = train[target]
X_valid = valid[feature_cols]
y_valid = valid[target]
X_test = test[feature_cols]
y_test = test[target]

model = LinearRegression()
model.fit(X_train, y_train)

valid['model_prediction'] = model.predict(X_valid)
test['model_prediction'] = model.predict(X_test)

# Naive baseline = same half-hour yesterday.
valid['naive_lag48'] = valid['lag_48']
test['naive_lag48'] = test['lag_48']

def metrics(actual, predicted, name):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    wape = np.abs(actual - predicted).sum() / np.abs(actual).sum() * 100
    print(f'{name}: MAE={mae:.2f}, RMSE={rmse:.2f}, WAPE={wape:.2f}%')

print('\nVALIDATION')
metrics(y_valid, valid['naive_lag48'], 'Naive lag-48')
metrics(y_valid, valid['model_prediction'], 'Linear Regression')

print('\nTEST')
metrics(y_test, test['naive_lag48'], 'Naive lag-48')
metrics(y_test, test['model_prediction'], 'Linear Regression')

joblib.dump({'model': model, 'feature_cols': feature_cols}, MODELS / 'portfolio_model.joblib')

test[['timestamp',target,'model_prediction','naive_lag48']].to_csv(PROCESSED / 'test_predictions.csv', index=False)

plt.figure(figsize=(12,5))
plt.plot(test['timestamp'], test[target], label='Actual')
plt.plot(test['timestamp'], test['model_prediction'], label='Model')
plt.legend()
plt.title('Test: Actual vs Predicted')
plt.ylabel('Portfolio consumption kWh')
plt.tight_layout()
plt.savefig(FIGURES / 'actual_vs_predicted.png')
plt.close()

print('\nModel saved: models/portfolio_model.joblib')
