from data_pull import *
from data_format import *
from regressions import *

# Fred Testing
def choosing_series(fred):
    info1, df1 = fred.choose_random_series()
    print(info1.id, info1.title)

    info2, df2 = fred.choose_random_series()
    print(info2.id, info2.title)

def merging_series(fred):
    info1, df1 = fred.choose_random_series()
    print(info1.id, info1.title)

    info2, df2 = fred.choose_random_series()
    print(info2.id, info2.title)

    fin_df = pd.merge(df1, df2, how='outer', on=['date', 'realtime_start', 
                                                 'realtime_end'],
                            suffixes=("_" + info1.id, "_" + info2.id))
    print(fin_df.head())
    print("-------------------")
    print(fin_df)

def getting_random_formatted_data():
    raw, clean = get_merged_dfs_dense([("fred", 3)])
    print(raw)
    print("-------------------")
    print(clean)

def running_basic_regression():
    raw, clean = get_merged_dfs_dense([("fred", 2)], 30)
    print(raw)
    print("-------------------")
    print(clean)

    regr = Regression_Wrapper(raw, clean, "date")
    model = regr.run_linear_regression("test1", [3], 4)
    print("-------------------")
    print(type(regr.get_linear_regression_summary("test1")))
    print(regr.get_linear_regression_summary("test1"))
    
def saving_regressions():
    raw, clean = get_merged_dfs_dense([("fred", 2)], 20)
    print(raw)
    print("-------------------")
    print(clean)

    regr = Regression_Wrapper(raw, clean, "date")
    regr.run_linear_regression("test1", [3], 4)
    regr.run_linear_regression("test2", [4], 3)
    
    regr.write_regression_results_to_csv("test1", "test1.csv")
    regr.write_regression_results_to_csv("test2", "test1.csv")

if __name__ == "__main__":
    saving_regressions()



