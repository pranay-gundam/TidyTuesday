import pandas as pd
from data_pull import Fred, Bloomberg
from typing import List, Tuple
from pyfredapi import SeriesInfo
from functools import reduce

def reduce_format_dfs(dfs: List[pd.DataFrame], infos: List[Tuple[str, SeriesInfo]], 
                       sources: List[str]) -> pd.DataFrame:
    if len(dfs) != len(infos) or len(dfs) != len(sources) or len(infos) != len(sources):
        raise ValueError("All lists must be the same length.")

    for i in range(len(dfs)):
        columns_to_rename = {col: col + "_" + sources[i] + "_" + infos[i].id for col in dfs[i].columns if col.startswith("value")}
        dfs[i] = dfs[i].rename(columns=columns_to_rename)

    fin_df = reduce(lambda left, right: pd.merge(left, right, how='outer', on=['date', 'realtime_start', 
                                                               'realtime_end']), dfs)
    
    return fin_df, infos

def get_merged_dfs_raw(pull_info: List[Tuple[str, int]]) -> pd.DataFrame:
    """
    Given a list of tuples of the form (source, category_id), pull data from the
    sources and number of times specified in the tuples and merge the dataframes
    together.
    
    Parameters:
    pull_info: List of tuples of the form (source, number of series) where source is
    a string representing the source of the data and the number of series is how many
    series to pull from each respective source.
    
    Returns:
    A pandas DataFrame containing the merged data from the sources specified in 
    the pull_info list.
    """
    
    pull_info_str = str(pull_info)

    if "fred" in pull_info_str:
        fred = Fred()
    if "bloomberg" in pull_info_str:
        bloomberg = Bloomberg()
    
    infos = []
    dfs = []
    sources = []
    for source, times in pull_info:
        if source == "fred":
            for i in range(times):
                info, df = fred.choose_random_series()
                infos.append(info)
                dfs.append(df)
                sources.append("fred")
        elif source == "bloomberg":
            for i in range(times):
                info, df = bloomberg.choose_random_series()
                infos.append(info)
                dfs.append(df)
                sources.append("bloomberg")
        else:
            raise ValueError("Source not recognized.")
        
    raw, infos = reduce_format_dfs(dfs, infos, sources)
    return raw, infos

def get_merged_dfs_dense(pull_info: List[Tuple[str, int]], base_com_rows: int = 0) -> Tuple[pd.DataFrame, pd.DataFrame]:
    raw, infos = get_merged_dfs_raw(pull_info)
    
    while raw.dropna().shape[0] < base_com_rows:
        raw, infos = get_merged_dfs_raw(pull_info)
    
    return raw, raw.dropna(), infos
