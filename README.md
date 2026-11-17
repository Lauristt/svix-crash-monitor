# Weekly SVIX from Lauristt's HW3 pipeline

This public data branch supports the FINM 32800 class-report exhibit comparing option-implied equity volatility with trailing realized volatility. It contains only derived volatility and maturity metadata, not option quotes, settlement prices, or credentials.

- **Producer:** Lauristt's HW3 `monitor.compute_history` and `pull_es_options.pull_es_options`, at code commit `f777f5992af9066d1fb5c6e0f0cd9c830197fd24` in this repository.
- **Window:** May 1-October 31, 2026, committed in `settings.py`.
- **Sampling:** last FRED SP500 trading observation in each Friday-ending week; no forward filling. Holiday Fridays use the prior observed session.
- **Metric:** constant-30-calendar-day SVIX, in annualized percent. The HW3 engine interpolates total implied variance between the two month-end expiries used for the 30-day estimate, then takes its square root and multiplies by 100. Six of 27 weekly observations use extrapolation: the nearest expiry is 31-35 days away. The report explicitly flags these observations and checks the median gap excluding them. Risk-free rates come from FRED DGS1MO.
- **Columns:** `date`, `svix_30`, `days_near`, `days_far`. The CSV has eight significant digits, matching the HW3 monitor history convention.
- **Method:** Ian Martin (2017), *What Is the Expected Return on the Market?*, Quarterly Journal of Economics 132(1), 367-433, doi:10.1093/qje/qjw034.

The report reads `svix_weekly` with ChartBook from this branch's pinned commit and content hash. There is no build script in the manifest: readers need neither Databento nor WRDS. The live `monitor-history` branch and its daily workflow are unchanged.

## Regeneration (producer only)

Check out the producer code commit in a separate clone, install its locked environment with `uv sync --frozen`, and configure its Databento key locally. Run this branch's `rebuild.py --hw3-path /path/to/producer` using the producer's Python interpreter. The script imports the existing homework computation, uses the fixed settings in this branch, and retains the homework's zero-cost query guard. It writes only the derived CSV here; quotes remain in memory. A historical vendor revision can change recomputed numbers, so consumers should retain the report's pin until an intentional update is reviewed.
