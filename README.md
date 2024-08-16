# TidyTuesday

The TidyTuesday project is originally from the rfordatascience community in which a new dataset is published in a tidy format to be easy to work with that the community can use. My original intention was to post a blog series every tuesday by taking the published dataset and addressed some question using the dataset with some thoughtful analysis; this repo would host all the work to make the blog posts.

Since then, my economic interests have drastically changed and my primary interest is not running the regressions that I planned on before. Still, I wanted to do something with this repo and another friend and I have always joked about running random regressions to see what kind of weird interactions show up.

## How to run the code

### Pulling Data from Fred

The code is currently set up in a manner in which pulling data from fred requires the user to create a `.env` file to store their Fred API key. For instruction on how to request a Fred API key, click [here](https://fred.stlouisfed.org/docs/api/api_key.html).

To setup a `.env` file, simply create a new file in the same repository and name it `.env`. You will need to separate all api key information by a newline; to include the Fred api key, add the line `FRED_API_KEY=[your api key]` where you should replace the item in brackets (including the brackets themselves) by your fred api key.

### Pulling Data from Bloomberg

## Features to be added

- Pulling data from bloomberg
- Automating the latex report creation
- Script using `crontab` to automatically run reports each day
- Faster method to choose a random series from fred (iterating through all the categories each time from the root seems a bit extensive, could keep an ongoing list of series that I've tried and all available series and update this list periodically)
- Adding more features to the regression such as detrending, or other applied micro stuff that I just don't really know yet. Could ask some applied micro friends what they think.

## Ongoing issues and edgecases to solve

- Pulling the same dataframe twice (or more), unlikely but still possible
- Handle cases with too little usable merged data
- There still seem to be some edge case errors in the pulling random series (and iterating through a category tree), I've handled it so far by just retrying until something does work but this warrants another look.
- `reduce_format_dfs` currently only works for data pulled from the fred api just because of the way it's handling the formatting. On this note, a lot of the other function I suspect are not generalized as well. This is probably an issue to handle when adding other data sources
- There are instances in which you get dataframes whose dates don't coincide with eachother at all, as of right now I am just re-pulling data until I get two compatible series but still need to find a cleaner way to address this
