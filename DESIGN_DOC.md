# Design Document: wiki-finance-dq

## Why Monitor Wikipedia Pageviews?

Wikipedia pageview data for financial assets is a proxy signal for public attention. Quality issues in this data can silently corrupt downstream analysis:

- **Missing hours**: A scraper failure at hour 14 means daily totals are understated by ~4-8%
- **Zero-view days**: Suggest either a real anomaly (article renamed, redirect) or a collection failure
- **Coverage gaps**: If 100 articles are missing from a day's data, any "top movers" analysis is unreliable

## Checks

### 1. Coverage Check
For each date, verify:
- At least `min_articles_per_date` (default: 2000) articles are present
- Each article has at least `min_hours_per_article` (default: 20) hours of data

Missing articles typically indicate: Wikipedia dump file was incomplete, scraper filtered incorrectly, or article was renamed.

### 2. Missing & Zero Views
- **Null views**: Should be 0% — every row extracted from a valid dump has a view count
- **Zero-view rate**: Some articles legitimately get 0 views in off-peak hours; >5% zero article-days suggests a data issue

### 3. Spike Detection
For each article, compute a rolling Z-score of daily total views:
```
z = (today_views - article_mean) / article_std
```
Z > 3.0 → flag as spike.

These spikes are **valuable signals**, not bugs. A spike in `Tesla,_Inc.` on 2022-11-08 (Elon Musk Twitter acquisition) or `Bitcoin` on 2021-05-19 (crash day) is real data. The DQ system documents them so analysts can distinguish genuine events from collection failures.

## Baseline
On first run, per-article mean/std are saved to `configs/baseline_stats.json`. Subsequent runs compare against this baseline to detect long-term distribution drift (e.g., an article's popularity permanently increased after a major event).

## Alert Thresholds
| Check | Warning | Critical |
|---|---|---|
| Null views rate | > 5% | > 20% |
| Zero-view rate | > 5% | — |
| Coverage | < 2000 articles/day | — |
| Z-score spike | > 2.0 | > 3.0 |
