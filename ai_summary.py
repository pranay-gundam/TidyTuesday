import glob
import os
import sys
from typing import Optional

import anthropic
from dotenv import load_dotenv

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
    "Write 2-4 short paragraphs in plain, non-technical language summarizing what was tried "
    "this week and anything amusing, surprising, or notably strong/weak about the "
    "relationships found. Explicitly remind the reader that these are randomly paired series "
    "with no causal or rigorous statistical claim intended -- spurious correlation is the "
    "norm, not the exception, for this project.\n\n"
    "Output plain text only (no LaTeX commands, no markdown, no headers) -- it will be "
    "inserted directly into a LaTeX document body as prose paragraphs separated by blank lines."
)

LATEX_SPECIAL_CHARS = {
    "\\": r"\textbackslash{}",
    "%": r"\%",
    "$": r"\$",
    "&": r"\&",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _escape_latex(text: str) -> str:
    return "".join(LATEX_SPECIAL_CHARS.get(ch, ch) for ch in text)


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
        f"\\noindent {_escape_latex(note)}\n"
        "\\end{tcolorbox}\n"
    )


def generate_weekly_summary(file_path: str) -> None:
    """Regenerate weekly_summary.tex for the given week folder using Claude, based on
    all regression results and series descriptions recorded so far this week. Safe to
    call every day -- it overwrites the file each time so it always reflects the
    week-to-date, and by the time the week ends the final version is already in place.
    """
    weekly_summary_path = os.path.join(file_path, "weekly_summary.tex")

    load_dotenv()
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set; skipping AI weekly summary.", file=sys.stderr)
        with open(weekly_summary_path, "w") as f:
            f.write(_fallback_weekly_summary_tex("no ANTHROPIC_API_KEY configured"))
        return

    context = _read_week_context(file_path)
    if not context.strip():
        print(f"No regression data found in {file_path}; skipping AI weekly summary.", file=sys.stderr)
        with open(weekly_summary_path, "w") as f:
            f.write(_fallback_weekly_summary_tex("no data recorded yet this week"))
        return

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
        return

    with open(weekly_summary_path, "w") as f:
        f.write("\\section{Weekly Summary}\n\n")
        f.write(DISCLAIMER)
        f.write("\n")
        f.write(_escape_latex(summary_text))
        f.write("\n")
