import glob
import os
import sys
from typing import Optional

import anthropic
from dotenv import load_dotenv

from latex_utils import escape_latex

MODEL = "claude-opus-4-8"

DISCLAIMER = (
    "\\begin{tcolorbox}[colback=yellow!10,colframe=black!50,title=AI-Generated Content]\n"
    "\\noindent The summary below was written by Claude (Anthropic) from that week's "
    "regression outputs and series descriptions. It has not been reviewed or fact-checked "
    "by a human, and should be read as an automated, informal recap -- not analysis.\n"
    "\\end{tcolorbox}\n"
)

SYSTEM_PROMPT = (
    "You are writing a short, casual weekly recap for a hobby project that pulls random "
    "pairs of economic time series from FRED each day and runs a simple linear regression "
    "between them, purely for fun -- to see what odd correlations show up. You will be given "
    "that week's raw regression results (coefficients, p-values, R-squared) and the series "
    "descriptions involved.\n\n"
    "Each day produces TWO regressions between the same pair of series, distinguished in the "
    "CSV by model_name -- the plain date (e.g. '2026-07-20') is the RAW regression, run directly "
    "on the two series' levels; the same date with a '_detrended' suffix (e.g. "
    "'2026-07-20_detrended') is run on each series' residuals after regressing out its own "
    "linear time trend first. Two long series that both happen to drift in the same direction "
    "over time will show a 'significant' raw relationship for that reason alone, with no real "
    "link between them -- the detrended version strips that shared drift out, so a relationship "
    "that stays strong/significant there is much better evidence of a genuine relationship than "
    "one that only shows up in the raw regression. When you discuss a day's result, compare the "
    "two: a raw hit that collapses once detrended is exactly the kind of trend-mirage this "
    "project loves to dunk on, while a relationship that holds up in both is worth calling out "
    "as the rarer, more interesting case.\n\n"
    "Write 2-4 short paragraphs in plain, non-technical language summarizing what was tried "
    "this week and anything amusing, surprising, or notably strong/weak about the "
    "relationships found. Although you should point out and theorize about any strong relationships that are found, you shoul also explicitly remind the reader that these are randomly paired series "
    "with no causal or rigorous statistical claim intended -- spurious correlation is the "
    "norm, not the exception, for this project.\n\n"
    "Write in a cringely, sarcastically funny tone -- lean into deadpan irony, overly dramatic "
    "reactions to mundane statistics, and self-aware jokes about how silly it is to draw "
    "conclusions from randomly paired economic data. Don't be mean-spirited or punch down at "
    "the reader; the humor should come from embracing the absurdity of the exercise itself.\n\n"
    "Output plain text only (no LaTeX commands, no markdown, no headers) -- it will be "
    "inserted directly into a LaTeX document body as prose paragraphs separated by blank lines."
)

def _read_week_context(file_path: str) -> str:
    parts = []

    csv_path = os.path.join(file_path, "regression_summaries.csv")
    if os.path.isfile(csv_path):
        with open(csv_path, "r") as f:
            parts.append("Regression results so far this week (CSV):\n" + f.read())

    day_files = sorted(glob.glob(os.path.join(file_path, "tex_things", "day_*.tex")))
    for day_file in day_files:
        with open(day_file, "r") as f:
            parts.append(f.read())

    return "\n\n".join(parts)


def _fallback_weekly_summary_tex(reason: Optional[str] = None) -> str:
    note = "AI summary generation did not run successfully for this update"
    if reason:
        note += f" ({reason})"
    note += "."

    return (
        "\\section{Weekly Summary}\n\n"
        "\\begin{tcolorbox}[colback=yellow!10,colframe=black!50,title=AI-Generated Content]\n"
        f"\\noindent {escape_latex(note)}\n"
        "\\end{tcolorbox}\n"
    )


def generate_weekly_summary(file_path: str) -> bool:
    """Regenerate weekly_summary.tex for the given week folder using Claude, based on
    all regression results and series descriptions recorded so far this week. Safe to
    call every day -- it overwrites the file each time so it always reflects the
    week-to-date, and by the time the week ends the final version is already in place.

    Returns True if Claude actually wrote the summary, False if a fallback
    (disclaimer-only) file was written instead.
    """
    weekly_summary_path = os.path.join(file_path, "weekly_summary.tex")

    load_dotenv()
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set; skipping AI weekly summary.", file=sys.stderr)
        with open(weekly_summary_path, "w") as f:
            f.write(_fallback_weekly_summary_tex("no ANTHROPIC_API_KEY configured"))
        return False

    context = _read_week_context(file_path)
    if not context.strip():
        print(f"No regression data found in {file_path}; skipping AI weekly summary.", file=sys.stderr)
        with open(weekly_summary_path, "w") as f:
            f.write(_fallback_weekly_summary_tex("no data recorded yet this week"))
        return False

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": context}],
        )
        summary_text = "".join(block.text for block in response.content if block.type == "text").strip()
        if not summary_text:
            raise ValueError("empty response from model")
    except Exception as exc:
        print(f"AI weekly summary generation failed: {exc}", file=sys.stderr)
        with open(weekly_summary_path, "w") as f:
            f.write(_fallback_weekly_summary_tex(str(exc)))
        return False

    with open(weekly_summary_path, "w") as f:
        f.write("\\section{Weekly Summary}\n\n")
        f.write(DISCLAIMER)
        f.write("\n")
        f.write(escape_latex(summary_text))
        f.write("\n")

    return True
