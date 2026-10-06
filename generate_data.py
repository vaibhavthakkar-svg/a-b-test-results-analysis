"""
generate_data.py
----------------
Generates a synthetic A/B test dataset and saves it to ab_test_data.csv.

Columns:
    user_id    - unique user identifier
    group      - 'control' or 'treatment'
    converted  - 1 if the user converted, 0 otherwise
    timestamp  - simulated session timestamp
"""

import numpy as np
import pandas as pd

# Reproducibility
np.random.seed(42)

N_USERS = 10_000
CONTROL_RATE = 0.11     # 11% baseline conversion rate
TREATMENT_RATE = 0.124  # 12.4% conversion rate for new page

n_control = N_USERS // 2
n_treatment = N_USERS - n_control

# Assign groups
groups = ['control'] * n_control + ['treatment'] * n_treatment
np.random.shuffle(groups)

# Generate conversions
conversions = []
for g in groups:
    rate = CONTROL_RATE if g == 'control' else TREATMENT_RATE
    conversions.append(np.random.binomial(1, rate))

# Generate timestamps spread over 30 days
start_date = pd.Timestamp('2024-01-01')
timestamps = [
    start_date + pd.Timedelta(seconds=int(s))
    for s in np.random.uniform(0, 30 * 24 * 3600, N_USERS)
]

df = pd.DataFrame({
    'user_id': range(1, N_USERS + 1),
    'group': groups,
    'converted': conversions,
    'timestamp': timestamps
})

df = df.sort_values('timestamp').reset_index(drop=True)
df.to_csv('ab_test_data.csv', index=False)

print(f"Dataset saved to ab_test_data.csv")
print(f"Total users : {len(df):,}")
print(f"Control     : {(df['group'] == 'control').sum():,}")
print(f"Treatment   : {(df['group'] == 'treatment').sum():,}")
print(df.head())