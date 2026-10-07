# Simple Energy Volume Forecasting Project

This project uses the supplied synthetic half-hourly energy data.

## Folder flow

`raw data -> cleaning -> EDA -> features -> model -> evaluation -> 14-day forecast`

## Setup

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_all.py
```

On Windows activate with:

```bash
.venv\\Scripts\\activate
```

## Run one stage at a time

```bash
python src/01_data_overview.py
python src/02_clean_data.py
python src/03_eda.py
python src/04_build_features.py
python src/05_train_evaluate.py
python src/06_future_forecast.py
```

## Main output

`output/14_day_portfolio_forecast.csv`

## Model

A simple Linear Regression model is used intentionally. It predicts total portfolio half-hourly consumption using calendar, weather, active-customer count and lag features. The future forecast is recursive: each predicted half-hour becomes available for the next lag calculation.
