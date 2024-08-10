from data_pull import *
from data_format import *

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




if __name__ == "__main__":
    getting_random_formatted_data()


