#!/bin/bash

# Get the current week and year
current_week=$(date +%V)
current_year=$(date +%Y)

old_week=$(date -d "last week" +%V)
old_year=$(date -d "last week" +%Y)

# Define the folder name
folder_name="week_${current_year}_${current_week}"
old_folder_name="week_${old_year}_${old_week}"

# Check if the folder exists and make a new one if it doesn't while moving the previous week to the archive
if [ ! -d "$folder_name" ]; then
    mkdir "$folder_name"
    mv "$old_folder_name" "archive/$current_year"
fi

