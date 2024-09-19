import sys
from data_format import *
from data_pull import *
from regressions import *
from tex_format import *

def main(cur_date, file_path, cur_week = None):
    raw, clean, infos = get_merged_dfs_dense([("fred", 2)], 20)
    
    regr = Regression_Wrapper(raw, clean, "date")
    regr.run_linear_regression(cur_date, [3], 4)
    regr.write_regression_results_to_csv(cur_date, f"{file_path}/regression_summaries.csv")
    regr.write_regression_latex(cur_date, f"{file_path}/tex_tables/regression_table_{cur_date}.tex")
    regr.save_plot_png(cur_date, f"{file_path}/plots/plot_{cur_date}.png")

    if cur_week != None:
        init_folder_tex(file_path, cur_date)

    daily_tex_update(file_path, cur_date, infos)

if __name__ == "__main__":
    # Read in arguments
    args = sys.argv[1:]  
    if len(args) >= 2:
        main(args[0], args[1], args[2])
    else:
        main(args[0], args[1])