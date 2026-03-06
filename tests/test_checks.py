"""Tests for wiki-finance-dq checks."""
import pandas as pd
import pytest
from datetime import date


CONFIG = {
    "thresholds": {
        "min_articles_per_date": 3,
        "min_hours_per_article": 20,
        "zscore_spike": 3.0,
        "zero_views_pct_warning": 0.05,
        "missing_rate_warning": 0.05,
        "missing_rate_critical": 0.20,
    }
}


def make_df(rows):
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def test_coverage_passes_with_full_data():
    from src.coverage_check import check_coverage
    rows = [
        {"date": "2024-01-01", "hour": h, "article": f"Art_{a}", "views": 10}
        for a in range(5) for h in range(24)
    ]
    df = make_df(rows)
    result = check_coverage(df, CONFIG)
    assert result["passed"] is True


def test_coverage_fails_with_too_few_articles():
    from src.coverage_check import check_coverage
    rows = [
        {"date": "2024-01-01", "hour": h, "article": "Art_1", "views": 10}
        for h in range(24)
    ]
    df = make_df(rows)
    result = check_coverage(df, CONFIG)
    assert result["dates_below_min_articles"] > 0


def test_missing_check_passes_clean_data():
    from src.missing_check import check_missing_and_zeros
    rows = [
        {"date": "2024-01-01", "hour": h, "article": f"A{i}", "views": 100}
        for i in range(5) for h in range(24)
    ]
    df = make_df(rows)
    result = check_missing_and_zeros(df, CONFIG)
    assert result["null_views_rate"] == 0.0
    assert result["passed"] is True


def test_spike_detector_finds_spike():
    from src.spike_detector import compute_daily_totals, detect_spikes
    rows = []
    for d in range(1, 29):
        rows.append({"date": f"2024-01-{d:02d}", "hour": 0, "article": "Bitcoin", "views": 100})
    # Add one massive spike
    rows.append({"date": "2024-01-29", "hour": 0, "article": "Bitcoin", "views": 10000})
    df = make_df(rows)
    daily = compute_daily_totals(df)
    result = detect_spikes(daily, CONFIG)
    assert result["total_spikes"] >= 1
    assert result["top_spikes"][0]["article"] == "Bitcoin"


def test_spike_detector_no_spikes_on_stable_data():
    from src.spike_detector import compute_daily_totals, detect_spikes
    rows = [
        {"date": f"2024-01-{d:02d}", "hour": 0, "article": "StableArticle", "views": 100 + d}
        for d in range(1, 30)
    ]
    df = make_df(rows)
    daily = compute_daily_totals(df)
    result = detect_spikes(daily, CONFIG)
    assert result["total_spikes"] == 0
