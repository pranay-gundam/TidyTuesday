import statsmodels.api as sm
import pandas as pd
from typing import List
import os
import csv

class Regression_Wrapper:
    def __init__(self, df_raw: pd.DataFrame, df_clean: pd.DataFrame, date_str: List[str] = ["date"]):
        self.df_raw = df_raw
        self.df_clean = df_clean
        self.date_str = date_str

        self.models = dict()
        self.model_summaries = dict()
        self.plots = dict()

    def get_raw(self) -> pd.DataFrame:
        return self.df_raw

    def get_clean(self) -> pd.DataFrame:
        return self.df_clean
    
    def run_linear_regression(self, model_name: str, x_cols: List[int], y_col: int, df_type: str = "clean") -> None:
        if df_type == "clean":
            df = self.df_clean
        else:
            df = self.df_raw
        
        X = df.iloc[:, x_cols]
        X = sm.add_constant(X)  # Adds a constant term to the predictor
        y = df.iloc[:, y_col]
        
        model = sm.OLS(y, X).fit()
        
        self.models[model_name] = model
        self.model_summaries[model_name] = model.summary()

    def get_linear_regression_summary(self, model_name: str) -> str:
        if model_name in self.model_summaries:
            return str(self.model_summaries[model_name])
        else:
            return "Model not found."
        
    def write_regression_results_to_csv(self, model_name: str, filepath: str) -> None:
        coefficients = self.models[model_name].params
        pvals = self.models[model_name].pvalues
        rsquared = self.models[model_name].rsquared
        fvalue = self.models[model_name].fvalue
        f_pvalue = self.models[model_name].f_pvalue
        conf_int = self.models[model_name].conf_int()
        summary = self.models[model_name].summary()

        # Extract notes from the summary
        notes = summary.extra_txt
        
        # Check if the file exists and if it is empty
        file_exists = os.path.isfile(filepath)
        is_empty = os.path.getsize(filepath) == 0 if file_exists else True

        with open(filepath, mode='a', newline='') as f:
            writer = csv.writer(f)

            # Write the header if the file is empty
            if is_empty:
                header = ['model_name', 'variable', 'value', 'pvalue', 'conf_int_lower', 'conf_int_upper', 'rsquared', 'fvalue', 'f_pvalue', 'notes']
                writer.writerow(header)

            # Write the data for each coefficient
            for idx, coef in coefficients.items():
                row = [
                    model_name,
                    idx,
                    coef,
                    float(pvals[idx]),
                    float(conf_int.loc[idx, 0]),
                    float(conf_int.loc[idx, 1]),
                    float(rsquared),
                    float(fvalue),
                    float(f_pvalue),
                    notes
                ]
                writer.writerow(row)

    def write_regression_latex(self, model_name: str, filepath: str) -> None:
        with open(filepath, mode='w') as f:
            f.write(self.model_summaries[model_name].as_latex())
    