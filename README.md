# A/B Test Results Analysis

A complete statistical analysis of an A/B test dataset examining whether a new website landing page improves user conversion rates. This project demonstrates data wrangling, SQL querying, hypothesis testing, and data visualization — all in a clean, reproducible Python workflow.

## Project Overview

A fictional e-commerce company ran an A/B test over several weeks. Users were randomly assigned to either:
- **Control group**: the existing landing page
- **Treatment group**: a redesigned landing page

The goal is to determine whether the new page leads to a statistically significant increase in conversions.

## Skills Demonstrated

- **Python**: pandas, scipy, matplotlib, seaborn, sqlite3
- **SQL**: data filtering, aggregation, and group-level summaries via SQLite
- **Statistics**: two-proportion z-test, p-value interpretation, confidence intervals
- **Data Visualization**: bar charts, conversion rate comparisons, distribution plots

## Files

| File | Description |
|------|-------------|
| `README.md` | Project overview and instructions |
| `generate_data.py` | Script to generate a realistic synthetic A/B test dataset |
| `analysis.py` | Full analysis: SQL queries, hypothesis test, visualizations |
| `ab_test_data.csv` | Generated dataset (created by running `generate_data.py`) |

## Setup & Usage

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ab-test-analysis.git
cd ab-test-analysis
```

### 2. Install dependencies

```bash
pip install pandas scipy matplotlib seaborn
```

### 3. Generate the dataset

```bash
python generate_data.py
```

This creates `ab_test_data.csv` with 10,000 simulated user sessions.

### 4. Run the analysis

```bash
python analysis.py
```

This will:
- Load the CSV into an in-memory SQLite database
- Run SQL queries to summarize the data
- Perform a two-proportion z-test
- Print results and statistical interpretation to the console
- Save visualizations as PNG files

## Results Summary

| Group | Users | Conversions | Conversion Rate |
|-------|-------|-------------|-----------------|
| Control | ~5,000 | ~550 | ~11.0% |
| Treatment | ~5,000 | ~620 | ~12.4% |

**Conclusion**: The treatment group shows a modest lift in conversion rate. The two-proportion z-test determines whether this difference is statistically significant at the 95% confidence level (α = 0.05). See console output from `analysis.py` for exact numbers and the final recommendation.

## Interpretation Guide

- **p-value < 0.05**: Reject the null hypothesis → the new page performs significantly differently
- **p-value ≥ 0.05**: Fail to reject the null hypothesis → insufficient evidence of a real difference
- **Confidence interval**: If it does not contain 0, the difference is statistically significant

## License

MIT