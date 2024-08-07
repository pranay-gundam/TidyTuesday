from fredapi import Fred
from dotenv import load_dotenv
import os
from datetime import date

FRED_CATEGORIES = ["Money, Banking, & Finance", "Population, Employment, & Labor Markets", "National Accounts", 
                   "Production & Business Activity", "Prices", "U.S. Regional Data", "International Data",
                   "Academic Data"]

FRED_CATEGORY_IDS = [32991, 10, 32992, 1, 32455, 3008, 32263, 33060]

def load_fred_obj():
    # Loading the .env file
    load_dotenv()

    # Store credentials from .env file
    FRED_API_KEY = os.getenv('FRED_API_KEY')

    fred = Fred(api_key=FRED_API_KEY)

    return fred


def update_series_list():
    fred = load_fred_obj()


    # Iterate through all the categories and write a csv file with
    # categories and series in a tuple
    for category in FRED_CATEGORIES:
        series_list = fred.search_by_category(category)
        series_list.to_csv(f'{category}.csv')


    # Save the list of series to a file
    series_list.to_csv('series_list.csv')


def pull_random_fred_series():

    fred = load_fred_obj()

    #df1 = fred.get_series('SP500')
    #df2 = fred.get_series('SP500')



# Testing
fred = load_fred_obj()

for i in FRED_CATEGORY_IDS:
    try:
        print(fred.search_by_category(i, order_by='series_id').head())
    except:
        print(f"Error with category {i}")   

# Alternative method is to just try random numbers until one works!