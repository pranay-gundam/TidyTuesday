import sys
from data_format import *
from data_pull import *
from regressions import *

def main(cur_date, file_path):
    raw, clean, infos = get_merged_dfs_dense([("fred", 2)], 20)
    
    regr = Regression_Wrapper(raw, clean, "date")
    regr.run_linear_regression(cur_date, [3], 4)
    regr.write_regression_results_to_csv(cur_date, f"{file_path}/regression_summaries.csv")
    regr.write_regression_latex(cur_date, f"{file_path}/tex_tables/regression_table_{cur_date}.tex")
    regr.save_plot_png(cur_date, f"{file_path}/plots/plot_{cur_date}.png")

if __name__ == "__main__":
    # Read in arguments
    args = sys.argv[1:]  
    main(args[0], args[1])