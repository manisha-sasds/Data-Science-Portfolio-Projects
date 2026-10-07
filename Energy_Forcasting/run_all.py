import subprocess
import sys

scripts = [
    'src/01_data_overview.py',
    'src/02_clean_data.py',
    'src/03_eda.py',
    'src/04_build_features.py',
    'src/05_train_evaluate.py',
    'src/06_future_forecast.py'
]

for script in scripts:
    print('\n' + '='*80)
    print('RUNNING:', script)
    print('='*80)
    subprocess.run([sys.executable, script], check=True)

print('\nPROJECT COMPLETED SUCCESSFULLY')
