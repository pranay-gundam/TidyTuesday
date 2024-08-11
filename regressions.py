import statsmodels.api as sm
import pandas as pd
from typing import List

class Regression_Info:
    def __init__(self, df_raw: pd.DataFrame, df_clean: pd.DataFrame, tokens: List[str], date_str: str = "date"):
        self.df_raw = df_raw
        self.df_clean = df_clean
        self.tokens = tokens
        self.date_str = date_str

        self.models = dict()
        self.model_summaries = dict()
        self.plots = dict()

    def get_raw(self) -> pd.DataFrame:
        return self.df_raw

    def get_clean(self) -> pd.DataFrame:
        return self.df_clean
    
    def get_tokens(self) -> List[str]:        
        return self.tokens
    
    def add_token(self, token: str) -> None:
        self.tokens.append(token)

    def run_linear_regression(self, model_name: str, y_col: str, x_cols: List[str], df_type: str = "clean") -> sm.OLS:
        if df_type == "clean":
            df = self.df_clean
        else:
            df = self.df_raw
        
        X = df[x_cols]
        X = sm.add_constant(X)  # Adds a constant term to the predictor
        y = df[y_col]
        
        model = sm.OLS(y, X).fit()
        
        self.models[model_name] = model
        self.model_summaries[model_name] = model.summary()

        return model

    def get_linear_regression_summary(self, model_name: str) -> str:
        if model_name in self.model_summaries:
            return str(self.model_summaries[model_name])
        else:
            return "Model not found."