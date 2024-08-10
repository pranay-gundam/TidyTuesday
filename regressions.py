from sklearn.linear_model import LinearRegression
import pandas as pd
from typing import List

class Regression_Info:
    def __init__(self, df_raw: pd.DataFrame, df_clean: pd.DataFrame, tokens: List[str], date_str: str = "date"):
        self.df_raw = df_raw
        self.df_clean = df_clean
        self.tokens = tokens
        self.date_str = date_str

        

    def get_raw(self) -> pd.DataFrame:
        return self.df_raw

    def get_clean(self) -> pd.DataFrame:
        return self.df_clean
    
    def get_tokens(self) -> List[str]:        
        return self.tokens
    
    def add_token(self, token: str):
        self.tokens.append(token)

def run_linear_regression(df: pd.DataFrame, y_col: str, x_cols: List[str]) -> LinearRegression:
    model = LinearRegression()
    model.fit(df[x_cols], df[y_col])
    return model

def get_linear_regression_summary(model: LinearRegression, df: pd.DataFrame, x_cols: List[str], y_col: str) -> dict:
    coef = model.coef_
    intercept = model.intercept_
    r_squared = model.score(df[x_cols], df[y_col])
    return {"Coefficient": coef, "Intercept": intercept, "R-Squared": r_squared}