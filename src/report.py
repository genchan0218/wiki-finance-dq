"""Generate HTML and JSON quality reports."""
from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path

log = logging.getLogger(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <title>Wiki Finance DQ Report — {report_date}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2em; max-width: 1100px; }}
    h1 {{ color: #1a1a2e; }}
    h2 {{ color: #16213e; border-bottom: 2px solid #e0e0e0; padding-bottom: 4px; }}
    .pass {{ color: #27ae60; font-weight: bold; }}
    .warn {{ color: #f39c12; font-weight: bold; }}
    .fail {{ color: #e74c3c; font-weight: bold; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 0.5em; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 0.9em; }}
    th {{ background-color: #f2f2f2; }}
    tr:nth-child(even) {{ background-color: #fafafa; }}
  </style>
</head>
<body>
  <h1>Wiki Finance DQ Report — {report_date}</h1>
  <p>Date range: <strong>{start_date}</strong> &rarr; <strong>{end_date}</strong> &nbsp;|&nbsp;
     Rows loaded: <strong>{total_rows:,}</strong> &nbsp;|&nbsp;
     Articles: <strong>{article_count}</strong></p>

  <h2>Coverage Check: <span class="{coverage_class}">{coverage_status}</span></h2>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Dates checked</td><td>{dates_checked}</td></tr>
    <tr><td>Dates below min articles ({min_articles})</td><td>{dates_below_min}</td></tr>
    <tr><td>Avg hours per article</td><td>{avg_hours:.1f}</td></tr>
    <tr><td>Articles with full 24h</td><td>{complete_24h}</td></tr>
  </table>

  <h2>Missing & Zero Views: <span class="{missing_class}">{missing_status}</span></h2>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Null views rate</td><td>{null_rate:.2%}</td></tr>
    <tr><td>Zero-view article-days</td><td>{zero_days:,}</td></tr>
    <tr><td>Zero-view rate</td><td>{zero_rate:.2%}</td></tr>
  </table>

  <h2>Top Attention Spikes (Z-score > {zscore_threshold})</h2>
  <p>These represent days where an article had unusually high traffic — likely driven by news events.</p>
  <table>
    <tr><th>Article</th><th>Date</th><th>Total Views</th><th>Z-Score</th></tr>
  {spike_rows}
  </table>
</body>
</html>
"""


def generate_report(results: dict, config: dict, output_dir: str = "outputs/reports") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    report_date = results["report_date"]

    json_path = f"{output_dir}/report_{report_date}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log.info("JSON report: %s", json_path)

    coverage = results.get("coverage", {})
    missing = results.get("missing", {})
    spikes = results.get("spikes", {})
    by_date = coverage.get("by_date", [])

    avg_hours = sum(r["avg_hours_per_article"] for r in by_date) / max(len(by_date), 1)
    complete_24h = sum(r["complete_24h_articles"] for r in by_date)

    spike_rows = ""
    for s in spikes.get("top_spikes", [])[:15]:
        spike_rows += f"<tr><td>{s['article']}</td><td>{s['date']}</td><td>{s['total_views']:,}</td><td>{s['zscore']:.1f}</td></tr>\n"

    html = HTML_TEMPLATE.format(
        report_date=report_date,
        start_date=results.get("start_date", ""),
        end_date=results.get("end_date", ""),
        total_rows=results.get("total_rows", 0),
        article_count=results.get("article_count", 0),
        coverage_class="pass" if coverage.get("passed") else "fail",
        coverage_status="PASSED" if coverage.get("passed") else "FAILED",
        dates_checked=coverage.get("total_dates_checked", 0),
        dates_below_min=coverage.get("dates_below_min_articles", 0),
        min_articles=config["thresholds"]["min_articles_per_date"],
        avg_hours=avg_hours,
        complete_24h=complete_24h,
        missing_class="pass" if missing.get("passed") else "fail",
        missing_status="PASSED" if missing.get("passed") else "FAILED",
        null_rate=missing.get("null_views_rate", 0),
        zero_days=missing.get("zero_view_article_days", 0),
        zero_rate=missing.get("zero_view_rate", 0),
        zscore_threshold=config["thresholds"]["zscore_spike"],
        spike_rows=spike_rows,
    )

    html_path = f"{output_dir}/report_{report_date}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    log.info("HTML report: %s", html_path)
    return html_path
