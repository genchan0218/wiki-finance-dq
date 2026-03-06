"""Load pageview data from DuckDB for a date range."""
from __future__ import annotations

import logging
from datetime import date

import duckdb
import pandas as pd

log = logging.getLogger(__name__)


def load_pageviews(duckdb_path: str, start_date: date, end_date: date) -> pd.DataFrame:
    """Load hourly pageviews for a date range from DuckDB."""
    log.info("Loading pageviews %s to %s from DuckDB...", start_date, end_date)
    con = duckdb.connect(duckdb_path, read_only=True)
    df = con.execute(
        """
        SELECT date, hour, article, views
        FROM hourly_pageviews
        WHERE date >= ? AND date <= ?
        """,
        [str(start_date), str(end_date)],
    ).fetchdf()
    con.close()
    df["date"] = pd.to_datetime(df["date"])
    log.info("Loaded %d rows, %d articles, %d dates",
             len(df), df["article"].nunique(), df["date"].nunique())
    return df


def load_expected_articles(stock_path: str, crypto_path: str) -> set[str]:
    """Return the set of article names we expect to see in the DB."""
    import csv
    articles = set()
    with open(stock_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            title = row["title"].strip()
            if title:
                articles.add(title.replace(" ", "_"))
    with open(crypto_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            wiki_title = row.get("wiki_title", "").strip()
            if wiki_title:
                articles.add(wiki_title.replace(" ", "_"))
    return articles
