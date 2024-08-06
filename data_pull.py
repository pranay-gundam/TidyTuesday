import fredapi as Fred
from dotenv import load_dotenv
import os
from datetime import date


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

    # use function search_by_category
    series_list = None

    # Save the list of series to a file
    series_list.to_csv('series_list.csv')


def pull_random_fred_series():

    fred = load_fred_obj()

    #df1 = fred.get_series('SP500')
    #df2 = fred.get_series('SP500')