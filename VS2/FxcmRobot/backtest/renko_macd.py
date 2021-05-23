import numpy as np

from robot.common import indicators
from backtesting import  Backtest
from backtesting.lib import TrailingStrategy

class RenkoMacdSystem(TrailingStrategy):
    cash = 25000
    pos_size = int(cash * 0.05)
    
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
        
        self.set_atr_periods(20)
        self.set_trailing_sl(1)
        
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
        if is_buy == True: self.buy(size=pos_size//price)
        elif is_buy == False: self.sell(size=pos_size//price)


from backtest.common import *
import pandas as pd

fp = "E:\Programming\Trading\Data\KHC.USUSD_Candlestick_1_M_BID_23.12.2020-15.05.2021.csv"
df = pd.read_csv(fp, parse_dates = ["Local time"],
                 date_parser=lambda x: pd.to_datetime(x, utc=True))
df = dukascopy_filter(df)
data = prepare_df(df)

backtest = Backtest(data, RenkoMacdSystem, cash=RenkoMacdSystem.cash,
                    commission=.002, hedging=True)
print(backtest.run())

backtest.plot()
