import pandas as pd

# Unify various input formats to same

def dukascopy_filter(df):
    df = df.copy()
    df.set_index('Local time', inplace = True)
    df.index.rename('Date', inplace = True)
    return df

def fxcm_filter(df):
    df = df.copy()
    df.columns = ['Open', 'Close', 'High', 'Low', 'Volume']
    return df

def alpha_vintage_filter(df):
    df = df.copy()
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    df.index.rename('Date', inplace = True)
    return df