# wiki-finance-dq

Data quality monitoring system for the `wiki-finance-lakehouse` dataset — 75.6M hourly Wikipedia pageview rows across 2,196 financial assets (stocks + crypto), 2015 → present.

## Checks

| Check | What it detects |
|---|---|
| **Coverage** | Missing articles per date, incomplete hours (< 20/24h) |
| **Missing/Zero** | Null view counts, articles with zero traffic |
| **Spike Detection** | Z-score anomalies per article — flags likely news-driven events |

## Quick Start
```bash
make install
make run                              # last 7 days
make run -- --lookback-days 30       # last 30 days
make test
```

## Output
- `outputs/reports/report_YYYY-MM-DD.html` — visual report with spike table
- `outputs/reports/report_YYYY-MM-DD.json` — machine-readable metrics

## Sample Spike Output
```
=== Top Attention Spikes ===
Bitcoin                          2021-05-19  views=  842,341  z=18.4
GameStop_Corp.                   2021-01-27  views=  634,291  z=15.2
Tesla,_Inc.                      2022-11-08  views=  521,003  z=12.7
```

## Tech Stack
- Python 3.11, pandas, duckdb, numpy, pyyaml
