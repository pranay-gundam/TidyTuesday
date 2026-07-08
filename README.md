# TidyTuesday

The TidyTuesday project is originally from the rfordatascience community in which a new dataset is published in a tidy format to be easy to work with that the community can use. My original intention was to post a blog series every tuesday by taking the published dataset and addressed some question using the dataset with some thoughtful analysis; this repo would host all the work to make the blog posts.

Since then, my economic interests have drastically changed and my primary interest is not running the regressions that I planned on before. Still, I wanted to do something with this repo and another friend and I have always joked about running random regressions to see what kind of weird interactions show up.

The pipeline now runs completely on its own: every day it pulls a couple of random FRED series, regresses one against the other, plots the result, and has Claude (Anthropic's AI) write a short weekly recap of what showed up. See [Automated daily runs](#automated-daily-runs-github-actions) below.

## Setup

Requires Python 3.10+.

```bash
python3 -m venv .venv_tidytuesday
source .venv_tidytuesday/bin/activate
pip install -r requirements.txt
```

`requirements.txt` pins exact versions of everything (pandas, numpy, statsmodels, seaborn, matplotlib, pyfredapi, python-dotenv, anthropic) that are known to work together — pandas/numpy in particular have been sensitive to version drift in the past, so prefer installing from this file over `pip install`-ing packages ad hoc.

### API keys

Two API keys are needed, one for pulling data and one for writing the weekly summary.

Create a `.env` file in the repo root (never commit this file — it's already in `.gitignore`) with each key on its own line:

```
FRED_API_KEY=your_fred_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

- **FRED_API_KEY** — used to pull series from FRED. Request one [here](https://fred.stlouisfed.org/docs/api/api_key.html).
- **ANTHROPIC_API_KEY** — used to generate the weekly summary. Get one from the [Anthropic Console](https://console.anthropic.com/); this is a separate, pay-as-you-go account from any Claude subscription. At the volume this project uses it (one short call per day), cost is a few cents a month.

### Pulling data from Bloomberg

Not yet implemented — see [Features to be added](#features-to-be-added).

## Running it

**Manually / locally:**

```bash
bash main_loop.sh
```

This figures out the current ISO week, creates/archives week folders as needed, runs `main_loop.py` (data pull → regression → plot → tex tables → AI weekly summary), and compiles that week's `main_file.tex` to PDF with `latexmk` if it's installed locally.

**Automatically:** see the next section — you don't need to run anything by hand day to day.

## Automated daily runs (GitHub Actions)

`.github/workflows/daily.yml` runs the full pipeline above once a day (`0 12 * * *` UTC) on GitHub's own infrastructure, then commits and pushes the day's outputs back to the repo — no local machine needs to be on. It also installs TeX Live fresh on the runner each time and compiles the current week's PDF.

GitHub Actions was chosen over a local cron job or Windows Task Scheduler specifically so this stays portable: the workflow runs identically no matter what OS you're on, so anyone who forks this repo gets the same automation for free.

**To enable it on your own fork:**

1. Make sure Actions are enabled for your repo (Settings → Actions → General).
2. Add two repository secrets (Settings → Secrets and variables → Actions → New repository secret):
   - `FRED_API_KEY`
   - `ANTHROPIC_API_KEY`
3. That's it — it'll run on the schedule above. To trigger it immediately (e.g. to test your setup), go to the Actions tab → "Daily TidyTuesday update" → "Run workflow".

## AI-written weekly summary

`weekly_summary.tex` is no longer written by hand. Each day's run calls `ai_summary.py`, which hands Claude that week's regression results (`regression_summaries.csv`) and series descriptions accumulated so far, and asks for a short, plain-language recap — explicitly reminding the reader that these are randomly paired series with no causal claim intended. The file is regenerated (overwritten) every day so it always reflects the week to date, and by the time the week ends the final version is already in place.

Every generated summary is preceded by a visible disclaimer box in the compiled PDF stating it was written by Claude and hasn't been reviewed by a human. If the API call fails for any reason (missing key, network issue, etc.), the rest of the daily pipeline still completes — `weekly_summary.tex` just falls back to the disclaimer box with a note that generation didn't succeed that day, rather than breaking the LaTeX build.

## Features to be added

- Store and report the series information as well (currently it's only rendered into the daily `.tex` files, not kept in structured form)
- Pulling data from Bloomberg
- Faster method to choose a random series from fred (iterating through all the categories each time from the root seems a bit extensive, could keep an ongoing list of series that I've tried and all available series and update this list periodically)
- Adding more features to the regression such as detrending, or other applied micro stuff that I just don't really know yet. Could ask some applied micro friends what they think.

## Ongoing issues and edgecases to solve

- Pulling the same dataframe twice (or more), unlikely but still possible
- Handle cases with too little usable merged data
- There still seem to be some edge case errors in the pulling random series (and iterating through a category tree), I've handled it so far by just retrying until something does work but this warrants another look.
- `reduce_format_dfs` currently only works for data pulled from the fred api just because of the way it's handling the formatting. On this note, a lot of the other function I suspect are not generalized as well. This is probably an issue to handle when adding other data sources
- There are instances in which you get dataframes whose dates don't coincide with eachother at all, as of right now I am just re-pulling data until I get two compatible series but still need to find a cleaner way to address this
