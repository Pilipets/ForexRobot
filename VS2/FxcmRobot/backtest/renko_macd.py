import numpy as np

from robot.common import indicators
from backtesting import  Backtest, Strategy
from backtesting.lib import TrailingStrategy

class RenkoMacdSystem(TrailingStrategy):
    cash = 250000
    pos_size = cash * 0.05
    
    def init(self):
        DF = self.data.df.copy()
        DF.rename(columns={'Open':'open', 'High':'high', 'Low':'low',
                           'Close':'close', 'Volume':'tickqty'}, inplace=True)

        DF = indicators.MACD(DF)
        DF['macd_slope'] = indicators.slope(DF['macd'])
        DF['macd_signal_slope'] = indicators.slope(DF['macd_signal'])
        self.data.df['macd_cross'] = (np.sign(DF["macd"] - DF["macd_signal"]) +
                           np.sign(DF["macd_slope"] - DF["macd_signal_slope"]))

        DF = indicators.ATR(DF, 20)
        self.data.df['bar_num'] = DF['bar_num']
        self.data.df['atr'] = DF['atr']

        self.macd_cross = self.I(lambda: self.data.df['macd_cross'], name='macd_cross')
        self.bar_num = self.I(lambda: self.data.df['bar_num'], name='bar_num')
        
        self.set_atr_periods(50)
        self.set_trailing_sl(2)
        
    def next(self):
        price = self.data.Close[-1]
        atr = self.data.atr[-1]

        if not self.position:  last_signal = None
        elif self.position.is_long: last_signal = "long"
        else: last_signal = "short"

        close, is_buy = False, None
        bar_num = self.data.bar_num[-1]
        crossover = self.data.macd_cross[-1]

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
        
        if atr > 0.1:
            if is_buy == True: self.buy(tp=price+1.5*atr, size=int(pos_size/price))
            elif is_buy == False: self.sell(tp=price-1.5*atr, size=int(pos_size/price))


from backtest.common import *
import pandas as pd

fp = "E:\Programming\Trading\Data\EBAY.USUSD_Candlestick_1_M_BID_01.07.2020-22.05.2021.csv"
df = pd.read_csv(fp, parse_dates = ["Local time"],
                 date_parser=lambda x: pd.to_datetime(x, utc=True, dayfirst=True))

df = dukascopy_filter(df)
data = prepare_df(df)

data2 = data
backtest = Backtest(data2, RenkoMacdSystem, cash=RenkoMacdSystem.cash,
                    commission=.002, hedging=True)
print(backtest.run())

backtest.plot(resample=False, filename="temp.html")
