import pandas as pd
import pyfredapi as pf
from dotenv import load_dotenv
import os
import random
from typing import Tuple

class Fred:
    def __init__(self, api_key: str = None):
        if api_key is None:
            load_dotenv()

            # Store credentials from .env file
            FRED_API_KEY = os.getenv('FRED_API_KEY')
            self.api_key = FRED_API_KEY
        else:
            self.api_key = api_key

    def get_category(self, category_id: int) -> dict:
        return pf.get_category(category_id=category_id, api_key=self.api_key)

    def get_category_children(self, category_id: int) -> dict:
        return pf.get_category_children(category_id=category_id, api_key=self.api_key)

    def choose_random_category(self, category_id: int = 0) -> Tuple[str, str]:
        children = self.get_category_children(category_id)["categories"]
        random_child = None
        
        while children:
            random_child = random.choice(children)
            children = self.get_category_children(random_child["id"])["categories"]
        
        if random_child is None:
            return None, None

        id = random_child["id"]
        name = random_child["name"]
            
        return id, name

    def get_category_series(self, category_id: int) -> dict:
        return pf.get_category_series(category_id=category_id, api_key=self.api_key)

    def get_series(self, series_id: str) -> pd.DataFrame:
        return pf.get_series(series_id, api_key=self.api_key)

    def choose_random_series(self, category_id:int = 0) -> Tuple[str, pd.DataFrame]:
        category_id, _ = self.choose_random_category(category_id)
        series_list = self.get_category_series(category_id)
        
        while not series_list:
            category_id, _ = self.choose_random_category(category_id)
            
            while category_id is None:
                category_id, _ = self.choose_random_category(category_id)

            series_list = self.get_category_series(category_id)
        
        series_keys = list(series_list.keys())
        series_id = random.choice(series_keys)

        return series_list[series_id], self.get_series(series_id)


class Bloomberg:
    def __init__(self):
        pass
