#!/bin/bash

# Choosing the right virtual environment
deactivate
source .venv_tidytuesday/bin/activate

# Get the current week and year and date
current_week=$(date +%V)
current_year=$(date +%Y)

old_week=$(date -d "last week" +%V)
old_year=$(date -d "last week" +%Y)

current_date=$(date +%Y-%m-%d)

# Define the folder name
folder_name="year_${current_year}_week_${current_week}"
old_folder_name="year_${old_year}_week_${old_week}"

# Check if the folder exists and make a new one if it doesn't while moving the previous week to the archive
if [ ! -d "$folder_name" ]; then
    mkdir "$folder_name"
    mkdir "$folder_name/plots"
    mkdir "$folder_name/tex_tables"
    mkdir "$folder_name/tex_things"
    mv "$old_folder_name" "Archive/$current_year/week_${old_week}/"
    
    # Run the Python script with arguments
    python3 main_loop.py "$current_date" "$folder_name" "$current_week"
else
    # Run the Python script with arguments
    python3 main_loop.py "$current_date" "$folder_name" 
fi


