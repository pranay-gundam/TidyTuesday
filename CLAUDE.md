# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo does

Pulls a couple of random economic time series from FRED each day, runs a simple linear
regression between them "just to see what weird interactions show up," and renders the results
(regression tables, a plot, series descriptions) into a per-week LaTeX report. Each week's report
also gets an AI-written summary paragraph (via the Anthropic API) recapping that week's findings,
clearly marked as AI-generated. The whole thing runs unattended once a day via GitHub Actions,
which commits the day's outputs back to the repo and compiles the week's PDF.

## Commands

```bash
# Setup
python3 -m venv .venv_tidytuesday
source .venv_tidytuesday/bin/activate
pip install -r requirements.txt          # exact pinned versions -- prefer this over ad-hoc installs

# Run the full daily pipeline manually (pull -> regress -> plot -> tex -> AI summary -> PDF)
bash main_loop.sh

# Run a single day's Python step directly (bypasses the week-folder/archive bash logic)
python3 main_loop.py <YYYY-MM-DD> <folder_name> [current_iso_week]   # 3rd arg only on the first day of a new week

# Manual smoke tests / scratch exploration (not a real test suite -- see tests.py)
python3 tests.py
```

There is no linter, formatter, or automated test suite configured. `tests.py` is a set of
manually-invoked, print-based smoke checks (edit `if __name__ == "__main__":` at the bottom to
pick which function runs) — it is not run in CI.

Two API keys are required, via a local `.env` (gitignored) for manual runs or as GitHub Actions
repo secrets for the scheduled workflow: `FRED_API_KEY` and `ANTHROPIC_API_KEY`. See README.md
for how to obtain each.

## Architecture

**Pipeline module chain** (`main_loop.py` orchestrates all of these for one day's run):

1. `data_pull.py` — `Fred` class wraps `pyfredapi`. `choose_random_series()` walks the FRED
   category tree from the root, descending into a random child category at each level until it
   hits a leaf, then picks a random series from that leaf category. Retries internally when a
   category/series turns out to be empty. `Bloomberg` class is a stub (not implemented).
2. `data_format.py` — `get_merged_dfs_raw` pulls N series from each requested source and
   outer-merges them on date; `reduce_format_dfs` renames value columns to
   `value_<source>_<series_id>` before merging (currently FRED-specific — see README's open
   issues). `get_merged_dfs_dense` retries the whole pull until the merged frame has at least
   `base_com_rows` fully-overlapping (non-NaN) rows, since randomly paired series often don't
   share a date range.
3. `regressions.py` — `Regression_Wrapper` holds both the raw and NaN-dropped ("clean") merged
   frames, runs an OLS via `statsmodels`, and has methods to dump the regression summary to CSV
   (`regression_summaries.csv`, appended to across the whole week) and LaTeX, and to save a
   `seaborn.regplot` PNG. Every day, two regressions are run for the same series pair, sharing a
   naming convention distinguished by `model_name`: the raw regression (`model_name` = the date,
   e.g. `2026-07-20`) via `run_linear_regression`, and a detrended regression
   (`model_name` = the date + `_detrended`, e.g. `2026-07-20_detrended`) via
   `run_detrended_regression`, which regresses each series on a date trend first and relates only
   the residuals. Two long series that share a drift will look "significant" in the raw
   regression for that reason alone — the detrended version exists so a relationship that
   survives having the shared trend removed is meaningfully stronger evidence than one that only
   shows up raw. `save_plot_png` (and the CSV/LaTeX writers) key off `model_name`, so both
   regressions' outputs land side by side in `regression_summaries.csv`/`tex_tables/`/`plots/`.
4. `tex_format.py` — assembles the per-week LaTeX document. `init_folder_tex` (called once, on
   the first day of a new week folder) writes `main_file.tex` from the templates in
   `tex_templates/` and a fresh `weekly_summary.tex` stub, with `\include`s pre-wired for all 7
   days of that ISO week. `daily_tex_update` writes that day's `tex_things/day_<date>.tex`
   section (series descriptions + raw regression table/plot + detrended regression table/plot,
   each labeled and captioned separately so the two are never confused).
5. `ai_summary.py` — `generate_weekly_summary(file_path)` is called at the end of every daily run
   (not just at week's end). It reads `regression_summaries.csv` (which now contains both the raw
   and `_detrended` rows per day) and every `tex_things/day_*.tex` written so far that week, sends
   that as context to `claude-opus-4-8` via the `anthropic` SDK, and overwrites
   `weekly_summary.tex` with the result — always prefixed by a `tcolorbox` disclaimer stating
   it's AI-generated. The system prompt explicitly teaches the raw-vs-detrended distinction and
   instructs the model to weigh a relationship that survives detrending as stronger evidence than
   one that only appears raw. Because it runs and overwrites daily, the file is always current and
   no special end-of-week detection is needed. On any failure (missing key, API/network error, no
   data yet) it writes a fallback disclaimer-only file instead of raising, so a bad AI call never
   breaks the LaTeX build or the rest of the daily pipeline. Returns `True`/`False` (AI summary vs.
   fallback) so `main_loop.py` can report it in the daily digest. Model output text is
   LaTeX-escaped before insertion — never write raw model output into a `.tex` file without going
   through `_escape_latex`.
6. `main_loop.py`'s `build_digest(...)` assembles a short markdown summary of the day's run
   (series pulled, regression R²/p-value, AI summary status) and writes it to `digest.txt` at the
   repo root (gitignored, overwritten every run). `main_loop.sh` appends a PDF-compile status
   line to that same file after the Python step finishes. The GitHub Actions workflow posts its
   contents as a comment on a persistent "Daily TidyTuesday Runs" issue (created on first use) —
   see the workflow's last step for the failure-path fallback when `digest.txt` never got
   written.

**Week-folder lifecycle** (`main_loop.sh`, the entry point for both manual and automated runs):
computes the current ISO year/week, and if `year_<YYYY>_week_<WW>/` doesn't exist yet, creates it
(with `plots/`, `tex_tables/`, `tex_things/` subfolders), archives the previous week's folder into
`Archive/<old_year>/week_<old_week>/`, and calls `main_loop.py` with the extra `cur_week` arg so
`main_loop.py` knows to run `init_folder_tex`. Otherwise it just calls `main_loop.py` for that
day. After the Python step, it best-effort compiles `main_file.tex` to PDF with `latexmk` if
available (skips silently if not — this matters for local runs, since only the GitHub Actions
runner has TeX Live installed via the workflow). The script activates `.venv_tidytuesday` for
local runs but skips that when `$GITHUB_ACTIONS` is set, since the Actions workflow installs
dependencies directly.

**Automation** (`.github/workflows/daily.yml`): runs `main_loop.sh` daily on a fresh Ubuntu
runner (with `FRED_API_KEY`/`ANTHROPIC_API_KEY` from repo secrets), installs TeX Live on the
runner each time, then commits and pushes the week folder + `Archive/` back to the repo. Chosen
over local cron/Task Scheduler specifically so the automation is portable to anyone who forks the
repo, regardless of their OS.

**Output layout**: active weeks live at the repo root as `year_<YYYY>_week_<WW>/`; once a new
week starts, the previous one moves to `Archive/<YYYY>/week_<WW>/`. Each week folder has the same
shape: `main_file.tex` (top-level document), `weekly_summary.tex` (AI-written), `plots/`,
`tex_tables/`, `tex_things/`, and `regression_summaries.csv`.
