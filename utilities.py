import pandas as pd


# HELPER 1: Converts stored JSON file into dataframe. *If df_in_json is None, returns empty dataframe
def json_to_df(df_in_json):
    if df_in_json is None:
        return pd.DataFrame()
    else:
        df = pd.read_json(df_in_json)
        if 'Time' not in df.columns:
            return df
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        df = df.sort_values('Time')
        return df