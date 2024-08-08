import pyfredapi as pf
from dotenv import load_dotenv
import os
from datetime import date
import random

FRED_CATEGORIES = ["Money, Banking, & Finance", "Population, Employment, & Labor Markets", "National Accounts", 
                   "Production & Business Activity", "Prices", "U.S. Regional Data", "International Data",
                   "Academic Data"]

FRED_CATEGORY_IDS = [32991, 10, 32992, 1, 32455, 3008, 32263, 33060]

class Fred:
    def __init__(self, api_key = None):
        if api_key is None:
            load_dotenv()

            # Store credentials from .env file
            FRED_API_KEY = os.getenv('FRED_API_KEY')
            self.api_key = FRED_API_KEY
        else:
            self.api_key = api_key

    def get_category(self, category_id):
        return pf.get_category(category_id=category_id, api_key=self.api_key)

    def get_category_children(self, category_id):
        return pf.get_category_children(category_id=category_id, api_key=self.api_key)

    def choose_random_category(self, category_id = 0):
        children = self.get_category_children(category_id)["categories"]
        id = None
        name = None
        while not children:
            random_child = random.choice(children)
            id = random_child["id"]
            name = random_child["name"]
            children = self.get_category_children(random_child["id"])["categories"]
        return id, name

    def get_category_series(self, category_id):
        return pf.get_category_series(category_id=category_id, api_key=self.api_key)

    def choose_random_series(self, category_id = 0):
        category_id, name = self.choose_random_category(category_id)
        series = self.get_category_series(category_id)["series"]

    def get_series(self, series_id):
        return pf.get_series(series_id="GDP", api_key=self.api_key)

def update_series_list(fred):
    # Iterate through all the categories and write a csv file with
    # categories and series in a tuple
    for category in FRED_CATEGORIES:
        series_list = fred.search_by_category(category)
        series_list.to_csv(f'{category}.csv')


    # Save the list of series to a file
    series_list.to_csv('series_list.csv')


def pull_random_fred_series(fred):
    pass
    #df1 = fred.get_series('SP500')
    #df2 = fred.get_series('SP500')



# Testing
fred = Fred()
FRED_API_KEY = os.getenv('FRED_API_KEY')
hello = pf.get_category_children(34009, FRED_API_KEY)
series = pf.get_category_series(34009, FRED_API_KEY)
print(hello)
print(series.keys())
