"""Check article and hour coverage per date."""
from __future__ import annotations

import pandas as pd


def check_coverage(df: pd.DataFrame, config: dict) -> dict:
    """
    Check:
    1. How many distinct articles appear per date (vs expected minimum)
    2. How many hours of data each article has per date (vs expected minimum)
    """
    min_articles = config["thresholds"]["min_articles_per_date"]
    min_hours = config["thresholds"]["min_hours_per_article"]

    results_by_date = []
    for dt, group in df.groupby("date"):
        article_count = group["article"].nunique()
        hours_per_article = group.groupby("article")["hour"].nunique()
        low_hour_articles = (hours_per_article < min_hours).sum()
        complete_articles = (hours_per_article >= 24).sum()

        results_by_date.append({
            "date": str(dt.date()),
            "article_count": int(article_count),
            "articles_below_min": int(article_count < min_articles),
            "low_hour_article_count": int(low_hour_articles),
            "complete_24h_articles": int(complete_articles),
            "avg_hours_per_article": round(float(hours_per_article.mean()), 2),
        })

    dates_below_min = sum(r["articles_below_min"] for r in results_by_date)

    return {
        "by_date": results_by_date,
        "dates_below_min_articles": dates_below_min,
        "total_dates_checked": len(results_by_date),
        "passed": dates_below_min == 0,
    }
