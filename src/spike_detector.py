"""Detect anomalous pageview spikes using Z-score per article."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)


def compute_daily_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate hourly → daily total views per article."""
    return (
        df.groupby(["date", "article"])["views"]
        .sum()
        .reset_index()
        .rename(columns={"views": "total_views"})
    )


def detect_spikes(daily_df: pd.DataFrame, config: dict) -> dict:
    """
    For each article, compute Z-score of its daily views.
    Flag any date where Z-score > threshold as a spike.

    Returns summary with top spikes (likely news events).
    """
    threshold = config["thresholds"]["zscore_spike"]
    spikes = []

    for article, group in daily_df.groupby("article"):
        if len(group) < 3:
            continue
        mean = group["total_views"].mean()
        std = group["total_views"].std()
        if std == 0:
            continue
        group = group.copy()
        group["zscore"] = (group["total_views"] - mean) / std
        flagged = group[group["zscore"] > threshold]
        for _, row in flagged.iterrows():
            spikes.append({
                "article": article,
                "date": str(row["date"].date()) if hasattr(row["date"], "date") else str(row["date"]),
                "total_views": int(row["total_views"]),
                "zscore": round(float(row["zscore"]), 2),
            })

    spikes.sort(key=lambda x: x["zscore"], reverse=True)
    return {
        "total_spikes": len(spikes),
        "top_spikes": spikes[:20],
        "threshold_used": threshold,
    }


def load_baseline(path: str) -> dict:
    p = Path(path)
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return {}


def save_baseline(stats: dict, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(stats, f, indent=2, default=str)
    log.info("Baseline saved to %s", path)


def compute_baseline_stats(daily_df: pd.DataFrame) -> dict:
    """Compute per-article mean/std for baseline comparison."""
    stats = {}
    for article, group in daily_df.groupby("article"):
        stats[article] = {
            "mean": float(group["total_views"].mean()),
            "std": float(group["total_views"].std()),
            "count": int(len(group)),
        }
    return stats
