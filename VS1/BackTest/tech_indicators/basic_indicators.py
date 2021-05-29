def ATR(df, period):
    df = df.copy()
    df['High-Low'] = abs(df['High'] - df['Low'])
    df['High-PrevClose'] = abs(df['High'] - df['Close'].shift(1))
    df['Low-PrevClose'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis = 1, skipna = False)
    df['ATR'] = df['TR'].rolling(period).mean()

    return df['ATR']

def BollingerBands(df, n, std):
    df = df.copy()
    df["MA"] = df['Close'].rolling(n).mean()
    df["M_std"] = df["MA"].rolling(n).std()
    df["BB_up"] = df["MA"] + std * df["M_std"]
    df["BB_dn"] = df["MA"] - std * df["M_std"]
    df["BB_percent"] = (df['Close'] - df['BB_dn']) / (df['BB_up'] - df['BB_dn'])
    df.drop(['M_std'], axis = 1, inplace = True)

    return df

def MACD(df, a = 12, b = 26, c = 9):
    df = df.copy()
    df["EMA_fast"]=df["Close"].ewm(span=a, min_periods=a).mean()
    df["EMA_slow"]=df["Close"].ewm(span=b, min_periods=b).mean()
    df["MACD"]= df["EMA_fast"] - df["EMA_slow"]
    df["MACD_sig"] = df["MACD"].ewm(span=c, min_periods=c).mean()
    df.drop(['EMA_fast', 'EMA_slow'], axis = 1, inplace = True)

    return df

import statsmodels.api as sm

def slope(ser, n):
    slopes = [0 for i in range(n-1)]
    for i in range(n, len(ser)+1):
        y = ser[i-n : i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)

from stocktrends import Renko
import numpy as np

def renko_DF(DF, atr_period, brick_size):
    df = DF.copy()
    df.reset_index(inplace=True)
    df.columns = ["date", "open", "high", "low", "close", "volume"]

    df2 = Renko(df)
    df2.brick_size = max(brick_size, round(ATR(DF, atr_period)[-1], 0))

    renko_df = df2.get_ohlc_data()
    renko_df["bar_num"] = np.where(renko_df["uptrend"]==True, 1 , np.where(renko_df["uptrend"] == False, -1, 0))

    for i in range(1, len(renko_df["bar_num"])):
        if np.sign(renko_df["bar_num"][i]) == np.sign(renko_df["bar_num"][i-1]):
            renko_df["bar_num"][i] += renko_df["bar_num"][i-1]

    renko_df.drop_duplicates(subset="date", keep="last", inplace=True)
    renko_df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'uptrend', 'bar_num']
    return renko_df