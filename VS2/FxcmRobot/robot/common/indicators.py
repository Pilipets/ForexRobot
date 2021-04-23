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

def renko_merge(DF):
    df = copy.deepcopy(DF)
    df["Date"] = df.index
    renko = renko_DF(df)
    renko.columns = ["Date","open","high","low","close","uptrend","bar_num"]
    merged_df = df.merge(renko.loc[:,["Date","bar_num"]],how="outer",on="Date")
    merged_df["bar_num"].fillna(method='ffill',inplace=True)
    merged_df["macd"]= MACD(merged_df,12,26,9)[0]
    merged_df["macd_sig"]= MACD(merged_df,12,26,9)[1]
    merged_df["macd_slope"] = slope(merged_df["macd"],5)
    merged_df["macd_sig_slope"] = slope(merged_df["macd_sig"],5)
    return merged_df