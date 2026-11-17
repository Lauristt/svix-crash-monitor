"""Rebuild the derived export using the student's original HW3 implementation."""

import argparse
import io
import runpy
import subprocess
import sys
from pathlib import Path

import pandas as pd
import requests

EXPORT_DIR = Path(__file__).resolve().parent
PUBLICATION = runpy.run_path(str(EXPORT_DIR / "settings.py"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hw3-path", type=Path, required=True)
    args = parser.parse_args()
    source = args.hw3_path.resolve()
    commit = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
    ).strip()
    if commit != PUBLICATION["SOURCE_COMMIT"]:
        raise ValueError("Check out the SOURCE_COMMIT declared in settings.py first")
    sys.path.insert(0, str(source / "src"))
    from monitor import compute_history
    from pull_es_options import pull_es_options
    from pull_fred import pull_fred

    start, end = PUBLICATION["START_DATE"], PUBLICATION["END_DATE"]
    response = requests.get(
        "https://fred.stlouisfed.org/graph/fredgraph.csv",
        params={"id": "SP500", "cosd": start, "coed": end},
        timeout=60,
    )
    response.raise_for_status()
    calendar = pd.read_csv(io.StringIO(response.text), na_values=".")
    calendar.columns = ["date", "SP500"]
    calendar["date"] = pd.to_datetime(calendar["date"])
    dates = (
        calendar.dropna()
        .set_index("date")
        .index.to_series()
        .resample("W-FRI")
        .max()
        .dropna()
    )
    dates = dates[(dates >= start) & (dates <= end)]
    rates = pull_fred(start_date="2026-04-01")
    rates = rates[rates.date <= end]
    rows = []
    for date in dates:
        day = date.strftime("%Y-%m-%d")
        following = (date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        options, _ = pull_es_options(day, following)
        result = compute_history(options[options.date == date], rates)
        if len(result) != 1:
            raise ValueError(f"Expected one computed session for {day}")
        rows.append(result[["date", "svix_30", "days_near", "days_far"]])
    export = pd.concat(rows, ignore_index=True).sort_values("date")
    export.to_csv(
        EXPORT_DIR / "svix_weekly.csv",
        index=False,
        float_format="%.8g",
        date_format="%Y-%m-%d",
    )
    print(
        f"Exported {len(export)} weekly observations through {export.date.max().date()}"
    )


if __name__ == "__main__":
    main()
