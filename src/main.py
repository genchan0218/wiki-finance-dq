"""Entry point for wiki-finance-dq data quality monitoring."""
from __future__ import annotations

import argparse
import logging
from datetime import date, timedelta

import yaml

from .coverage_check import check_coverage
from .loader import load_pageviews
from .missing_check import check_missing_and_zeros
from .report import generate_report
from .spike_detector import (
    compute_daily_totals,
    detect_spikes,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Wiki Finance Data Quality Monitor")
    parser.add_argument("--end-date", default=str(date.today() - timedelta(days=1)))
    parser.add_argument("--lookback-days", type=int, default=7)
    args = parser.parse_args()

    config = load_config()
    end_date = date.fromisoformat(args.end_date)
    start_date = end_date - timedelta(days=args.lookback_days - 1)

    log.info("DQ check: %s to %s", start_date, end_date)

    df = load_pageviews(config["data"]["duckdb_path"], start_date, end_date)

    log.info("Running coverage check...")
    coverage = check_coverage(df, config)

    log.info("Running missing/zero check...")
    missing = check_missing_and_zeros(df, config)

    log.info("Running spike detection...")
    daily = compute_daily_totals(df)
    spikes = detect_spikes(daily, config)

    results = {
        "report_date": str(end_date),
        "start_date": str(start_date),
        "end_date": str(end_date),
        "total_rows": len(df),
        "article_count": df["article"].nunique(),
        "coverage": coverage,
        "missing": missing,
        "spikes": spikes,
    }

    html_path = generate_report(results, config, config["output"]["reports_dir"])

    log.info("Done. Report: %s", html_path)
    log.info("Coverage: %s | Missing: %s | Spikes found: %d",
             "PASS" if coverage["passed"] else "FAIL",
             "PASS" if missing["passed"] else "FAIL",
             spikes["total_spikes"])

    if spikes["top_spikes"]:
        print("\n=== Top Attention Spikes ===")
        for s in spikes["top_spikes"][:10]:
            print(f"  {s['article']:40s} {s['date']}  views={s['total_views']:>8,}  z={s['zscore']:.1f}")


if __name__ == "__main__":
    main()
