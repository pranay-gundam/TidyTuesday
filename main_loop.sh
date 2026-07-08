#!/bin/bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

# Activate the local venv only for local/manual runs. In GitHub Actions,
# dependencies are installed directly onto the runner (see
# .github/workflows/daily.yml), so there's no venv to activate.
if [ -z "${GITHUB_ACTIONS:-}" ] && [ -f ".venv_tidytuesday/bin/activate" ]; then
    source .venv_tidytuesday/bin/activate
fi

# Get the current week and year and date
current_week=$(date +%V)
current_year=$(date +%Y)
current_date=$(date +%Y-%m-%d)

# Define the folder name
folder_name="year_${current_year}_week_${current_week}"

if [ ! -d "$folder_name" ]; then
    is_new_week=true
    mkdir -p "$folder_name/plots" "$folder_name/tex_tables" "$folder_name/tex_things"
else
    is_new_week=false
fi

# Archive every week folder sitting at the repo root that isn't the current week --
# this sweeps up both the week that just ended and any older leftover folders that
# were never archived (e.g. weeks from before this automation existed).
shopt -s nullglob
for dir in year_*_week_*/; do
    dir="${dir%/}"
    [ "$dir" = "$folder_name" ] && continue

    week_year="${dir#year_}"
    week_year="${week_year%%_week_*}"
    week_num="${dir##*_week_}"

    mkdir -p "Archive/$week_year"
    mv "$dir" "Archive/$week_year/week_${week_num}"
done
shopt -u nullglob

if [ "$is_new_week" = true ]; then
    python3 main_loop.py "$current_date" "$folder_name" "$current_week"
else
    python3 main_loop.py "$current_date" "$folder_name"
fi

# Compile the current week's PDF, if a LaTeX toolchain is available. Best-effort:
# a missing/broken LaTeX install shouldn't fail the whole daily run. Appends a
# status line to digest.txt (written by main_loop.py) for the daily notification.
if command -v latexmk >/dev/null 2>&1; then
    if (cd "$folder_name" && latexmk -pdf -interaction=nonstopmode -halt-on-error main_file.tex); then
        echo "**PDF:** compiled" >> digest.txt
    else
        echo "Warning: PDF compile failed for $folder_name" >&2
        echo "**PDF:** compile failed -- see workflow logs" >> digest.txt
    fi
else
    echo "latexmk not found; skipping PDF compile for $folder_name" >&2
    echo "**PDF:** skipped (latexmk not installed)" >> digest.txt
fi
