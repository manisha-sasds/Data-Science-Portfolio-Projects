from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROCESSED = Path('data/processed')
FIGURES = Path('reports/figures')
FIGURES.mkdir(parents=True, exist_ok=True)

cons = pd.read_csv(PROCESSED / 'consumption_clean.csv', parse_dates=['timestamp'])

print('\nConsumption statistics')
print(cons['consumption_kwh'].describe())

print('\nReading types')
print(cons['reading_type'].value_counts())

# Top 10 customers
top10 = (cons.groupby('customer_id')['consumption_kwh']
         .sum()
         .sort_values(ascending=False)
         .head(10))
print('\nTop 10 customers by consumption')
print(top10)

top10.sort_values().plot(kind='barh', figsize=(8,5), title='Top 10 Customers by Total Consumption')
plt.xlabel('Consumption kWh')
plt.tight_layout()
plt.savefig(FIGURES / 'top10_customers.png')
plt.close()

# Portfolio half-hourly demand
portfolio = cons.groupby('timestamp', as_index=False)['consumption_kwh'].sum()
portfolio.plot(x='timestamp', y='consumption_kwh', figsize=(12,5), title='Portfolio Half-Hourly Consumption')
plt.ylabel('kWh')
plt.tight_layout()
plt.savefig(FIGURES / 'portfolio_consumption.png')
plt.close()

# Daily demand
daily = portfolio.set_index('timestamp')['consumption_kwh'].resample('D').sum()
daily.plot(figsize=(12,5), title='Daily Portfolio Consumption')
plt.ylabel('kWh')
plt.tight_layout()
plt.savefig(FIGURES / 'daily_consumption.png')
plt.close()

print('\nEDA charts saved in reports/figures/')
