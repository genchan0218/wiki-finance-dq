"""Check for missing values and zero-view articles."""
from __future__ import annotations

import pandas as pd


def check_missing_and_zeros(df: pd.DataFrame, config: dict) -> dict:
    """
    Check:
    1. Null views rate
    2. Articles with zero total views on a given day
    """
    zero_warn = config["thresholds"]["zero_views_pct_warning"]
    miss_warn = config["thresholds"]["missing_rate_warning"]
    miss_crit = config["thresholds"]["missing_rate_critical"]

    total_rows = len(df)
    null_views = df["views"].isna().sum()
    null_rate = null_views / total_rows if total_rows > 0 else 0.0

    # Daily totals per article
    daily = df.groupby(["date", "article"])["views"].sum().reset_index()
    zero_rows = (daily["views"] == 0).sum()
    zero_rate = zero_rows / len(daily) if len(daily) > 0 else 0.0

    warnings = []
    criticals = []

    if null_rate > miss_crit:
        criticals.append(f"Null views rate {null_rate:.1%} exceeds critical threshold")
    elif null_rate > miss_warn:
        warnings.append(f"Null views rate {null_rate:.1%} exceeds warning threshold")

    if zero_rate > zero_warn:
        warnings.append(f"Zero-view rate {zero_rate:.1%} across article-days")

    return {
        "total_rows": total_rows,
        "null_views_count": int(null_views),
        "null_views_rate": round(float(null_rate), 6),
        "zero_view_article_days": int(zero_rows),
        "zero_view_rate": round(float(zero_rate), 6),
        "warnings": warnings,
        "criticals": criticals,
        "passed": len(criticals) == 0,
    }
