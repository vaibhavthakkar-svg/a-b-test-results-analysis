"""
analysis.py
-----------
Loads the A/B test dataset into SQLite, runs summary queries,
performs a two-proportion z-test, and produces visualizations.
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# ── 0. Style ──────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
ALPHA = 0.05  # significance level

# ── 1. Load data into SQLite ───────────────────────────────────────────────────
df = pd.read_csv('ab_test_data.csv', parse_dates=['timestamp'])

conn = sqlite3.connect(':memory:')
df.to_sql('ab_test', conn, index=False, if_exists='replace')

print("=" * 55)
print("  A/B TEST RESULTS ANALYSIS")
print("=" * 55)

# ── 2. SQL: group-level summary ────────────────────────────────────────────────
query_summary = """
SELECT
    "group",
    COUNT(*)                          AS total_users,
    SUM(converted)                    AS total_conversions,
    ROUND(AVG(converted) * 100, 2)    AS conversion_rate_pct
FROM ab_test
GROUP BY "group"
ORDER BY "group";
"""

summary = pd.read_sql_query(query_summary, conn)
print("\n[SQL] Group Summary:")
print(summary.to_string(index=False))

# ── 3. SQL: daily conversion trends ───────────────────────────────────────────
query_daily = """
SELECT
    DATE(timestamp)   AS day,
    "group",
    COUNT(*)          AS users,
    SUM(converted)    AS conversions,
    ROUND(AVG(converted) * 100, 2) AS conv_rate_pct
FROM ab_test
GROUP BY day, "group"
ORDER BY day, "group";
"""

daily = pd.read_sql_query(query_daily, conn)
conn.close()

# ── 4. Extract values for hypothesis test ──────────────────────────────────────
ctrl  = summary[summary['group'] == 'control'].iloc[0]
treat = summary[summary['group'] == 'treatment'].iloc[0]

n_ctrl  = int(ctrl['total_users'])
n_treat = int(treat['total_users'])
conv_ctrl  = int(ctrl['total_conversions'])
conv_treat = int(treat['total_conversions'])

p_ctrl  = conv_ctrl  / n_ctrl
p_treat = conv_treat / n_treat

# ── 5. Two-proportion z-test ───────────────────────────────────────────────────
# Pooled proportion under H0
p_pool = (conv_ctrl + conv_treat) / (n_ctrl + n_treat)
se = np.sqrt(p_pool * (1 - p_pool) * (1/n_ctrl + 1/n_treat))
z_stat = (p_treat - p_ctrl) / se
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))  # two-tailed

# 95% confidence interval for the difference
se_diff = np.sqrt(p_ctrl*(1-p_ctrl)/n_ctrl + p_treat*(1-p_treat)/n_treat)
z_crit  = stats.norm.ppf(1 - ALPHA / 2)
ci_low  = (p_treat - p_ctrl) - z_crit * se_diff
ci_high = (p_treat - p_ctrl) + z_crit * se_diff

print("\n[Hypothesis Test] Two-Proportion Z-Test")
print(f"  H0: p_treatment = p_control  (no difference)")
print(f"  H1: p_treatment ≠ p_control  (two-tailed, α = {ALPHA})")
print(f"\n  Control   conversion rate : {p_ctrl*100:.2f}%  ({conv_ctrl}/{n_ctrl})")
print(f"  Treatment conversion rate : {p_treat*100:.2f}%  ({conv_treat}/{n_treat})")
print(f"  Absolute lift             : {(p_treat-p_ctrl)*100:+.2f} pp")
print(f"  Relative lift             : {(p_treat-p_ctrl)/p_ctrl*100:+.1f}%")
print(f"\n  Z-statistic : {z_stat:.4f}")
print(f"  P-value     : {p_value:.4f}")
print(f"  95% CI for difference: [{ci_low*100:.3f} pp, {ci_high*100:.3f} pp]")

print("\n" + "=" * 55)
if p_value < ALPHA:
    print("  RESULT: STATISTICALLY SIGNIFICANT")
    print(f"  p = {p_value:.4f} < α = {ALPHA}")
    print("  Reject H0.")
    if p_treat > p_ctrl:
        print("  RECOMMENDATION: Deploy the new landing page.")
        print("  The treatment page produces a significantly higher")
        print("  conversion rate than the control page.")
    else:
        print("  RECOMMENDATION: Keep the original landing page.")
        print("  The treatment page performs significantly WORSE.")
else:
    print("  RESULT: NOT STATISTICALLY SIGNIFICANT")
    print(f"  p = {p_value:.4f} ≥ α = {ALPHA}")
    print("  Fail to reject H0.")
    print("  RECOMMENDATION: Do not switch pages based on this data.")
    print("  Consider running the test longer to gather more evidence.")
print("=" * 55)

# ── 6. Visualization 1: Conversion Rate Bar Chart ─────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("A/B Test Results", fontsize=14, fontweight='bold')

groups_labels = ['Control', 'Treatment']
rates = [p_ctrl * 100, p_treat * 100]
colors = ['#5B8DB8', '#E07B54']

bars = axes[0].bar(groups_labels, rates, color=colors, width=0.5, edgecolor='white')
axes[0].set_title("Conversion Rate by Group")
axes[0].set_ylabel("Conversion Rate (%)")
axes[0].set_ylim(0, max(rates) * 1.3)

for bar, rate in zip(bars, rates):
    axes[0].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.2,
        f"{rate:.2f}%",
        ha='center', va='bottom', fontweight='bold'
    )

# Significance annotation
sig_text = f"p = {p_value:.4f}\n{'Significant ✓' if p_value < ALPHA else 'Not Significant ✗'}"
axes[0].text(0.5, 0.90, sig_text, transform=axes[0].transAxes,
             ha='center', fontsize=10,
             color='green' if p_value < ALPHA else 'red')

# ── 7. Visualization 2: Daily Conversion Trend ────────────────────────────────
daily['day'] = pd.to_datetime(daily['day'])

for grp, color, label in zip(['control', 'treatment'], colors, ['Control', 'Treatment']):
    subset = daily[daily['group'] == grp]
    axes[1].plot(subset['day'], subset['conv_rate_pct'],
                 marker='o', markersize=3, color=color, label=label, linewidth=1.5)

axes[1].set_title("Daily Conversion Rate Over Time")
axes[1].set_ylabel("Conversion Rate (%)")
axes[1].set_xlabel("Date")
axes[1].legend()
axes[1].tick_params(axis='x', rotation=30)

plt.tight_layout()
plt.savefig('ab_test_results.png', dpi=150, bbox_inches='tight')
print("\nVisualization saved to ab_test_results.png")
plt.show()