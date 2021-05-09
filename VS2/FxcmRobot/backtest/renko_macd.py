import pandas as pd
import numpy as np

from robot.common import indicators
from backtesting import Strategy, Backtest
from backtesting.lib import resample_apply

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

class RenkoMacdSystem(Strategy):
    cash = 5000
    pos_size = cash * 0.03

    def macd_cross(self, df):
        df = indicators.MACD(df)
        df['macd_slope'] = indicators.slope(df['macd'])
        df['macd_signal_slope'] = indicators.slope(df['macd_signal'])
        
        return (np.sign(df["macd"] - df["macd_signal"]) +
                np.sign(df["macd_slope"] - df["macd_signal_slope"]))
    
    def init(self):
        df = self.data.df.copy()
        df.rename(columns={'Open':'open', 'High':'high', 'Low':'low',
                           'Close':'close', 'Volume':'tickqty'}, inplace=True)

        df = indicators.MACD(df)
        df['macd_slope'] = indicators.slope(df['macd'])
        df['macd_signal_slope'] = indicators.slope(df['macd_signal'])
        df['macd_cross'] = (np.sign(df["macd"] - df["macd_signal"]) +
                           np.sign(df["macd_slope"] - df["macd_signal_slope"]))

        df = indicators.ATR(df)

        self.macd_cross = self.I(lambda: df['macd_cross'], name='macd_cross')
        self.bar_num = self.I(lambda: df['bar_num'], name='bar_num')
        self.atr = self.I(lambda: df['atr'], name='atr')
        
    def next(self):
        df = self.data
        price = self.data.Close[-1]
        atr = self.atr[-1]

        if not self.position:  last_signal = None
        elif self.position.is_long: last_signal = "long"
        else: last_signal = "short"

        close, is_buy = False, None
        bar_num = self.bar_num[-1]
        crossover = self.macd_cross[-1]

        if last_signal is None:
            if bar_num >= 2 and crossover == 2: is_buy = True
            elif bar_num <= -2 and crossover == -2: is_buy = False
            
        elif last_signal == "long":
            if bar_num <= -2 and crossover == -2: close, is_buy = True, False
            elif crossover == -2: close = True
            
        elif last_signal == "short":
            if bar_num >= 2 and crossover == 2: close, is_buy = True, True
            elif crossover == 2: close = True

        if close: self.position.close()

        pos_size= RenkoMacdSystem.pos_size
        if is_buy == True: self.buy(size=pos_size/price, sl=price - atr)
        elif is_buy == False: self.sell(size=pos_size/price, sl=price + atr)

from backtesting.test import GOOG

data = prepare_df(GOOG)
backtest = Backtest(data, RenkoMacdSystem, cash=RenkoMacdSystem.cash, commission=.002, hedging=True)
print(backtest.run())

backtest.plot()