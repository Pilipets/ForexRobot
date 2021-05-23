from robot.common import indicators
import pandas as pd

def prepare_df(df):
    df = df.copy()
    df.rename(columns={'Open':'open', 'High':'high', 'Low':'low',
                       'Close':'close', 'Volume':'tickqty'}, inplace=True)
    df.index.names = ['date']

    renko_df = indicators.RenkoDF(df)
    df = df.merge(renko_df.loc[:,["date", "bar_num"]], how="outer", on="date")
    df["bar_num"].fillna(method = 'ffill', inplace = True)

    df.rename(columns={'open':'Open', 'high':'High', 'low':'Low',
             'close':'Close', 'date':'Index', 'tickqty':'Volume'}, inplace=True)
    df.set_index('Index', inplace=True)
    return df

def dukascopy_filter(df):
    df = df.copy()
    df.set_index('Local time', inplace = True)
    df.index.rename('Date', inplace = True)
    return df
