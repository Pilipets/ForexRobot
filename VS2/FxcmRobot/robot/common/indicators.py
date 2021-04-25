import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

def ATR(df, period = 20):
    df['tr_hl'] = abs(df['high'] - df['low'])
    df['tr_hp'] = abs(df['high'] - df['close'].shift(1))
    df['tr_lp'] = abs(df['low'] - df['close'].shift(1))
    df['tr'] = df[['tr_hl', 'tr_hp', 'tr_lp']].max(axis = 1)
    df['atr'] = df['tr'].rolling(period).mean()

    df.drop(['tr_hl', 'tr_hp', 'tr_lp', 'tr'], axis=1, inplace=True)
    return df

def MACD(df, fast = 12, slow = 26, macd_period = 9):
    df["macd_fast"] = df["close"].ewm(span=fast, min_periods=fast).mean()
    df["macd_slow"] = df["close"].ewm(span=slow, min_periods=slow).mean()
    df["macd"]= df["macd_fast"] - df["macd_slow"]
    df["macd_signal"] = df["macd"].ewm(span=macd_period, min_periods=macd_period).mean()

    df.drop(['macd_fast', 'macd_slow'], axis=1, inplace=True)
    return df

def BollingerBands(df, period = 20, std = 2):
    df["bbands_ma"] = df['close'].rolling(period).mean()
    df["bbands_std"] = df["bbands_ma"].rolling(period).std()
    df["bbands_up"] = df["bbands_ma"] + std * df["bbands_std"]
    df["bbands_dn"] = df["bbands_ma"] - std * df["bbands_std"]
    df["bbands_percent"] = (df['close'] - df['bbands_dn']) / (df['bbands_up'] - df['bbands_dn'])
    
    df.drop(['bbands_ma', 'bbands_std', 'bbands_up', 'bbands_dn'], axis=1, inplace=True)
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

def RenkoDF(df, atr_period = 120, brick_size = 0.5):
    atr_brick_size = ATR(df).iloc[-1]['atr']

    df.drop('atr', axis=1, inplace=True)
    df.reset_index(inplace=True)

    renko = Renko(df)
    renko.brick_size = min(atr_brick_size, brick_size)
    renko_df = renko.get_ohlc_data()

    renko_df["bar_num"] = np.where(renko_df["uptrend"]==True, 1 , np.where(renko_df["uptrend"] == False, -1, 0))

    for i in range(1, len(renko_df)):
        if np.sign(renko_df.loc[i, ("bar_num")]) == np.sign(renko_df.loc[i-1, ("bar_num")]):
            renko_df.loc[i, ("bar_num")] += renko_df.loc[i-1, ("bar_num")]

    renko_df.drop_duplicates(subset="date", keep="last", inplace=True)
    return renko_df