import numpy as np

from robot.common import indicators
from backtesting import  Backtest, Strategy
from backtesting.lib import TrailingStrategy

class BbandMacdSystem(Strategy):
    cash = 25000
    pos_size = cash * 0.03
    
    def init(self):
        DF = self.data.df.copy()
        DF.rename(columns={'Open':'open', 'High':'high', 'Low':'low',
                           'Close':'close', 'Volume':'tickqty'}, inplace=True)

        DF = indicators.MACD(DF)
        DF['macd_slope'] = indicators.slope(DF['macd'])
        DF['macd_signal_slope'] = indicators.slope(DF['macd_signal'])
        self.data.df['macd_cross'] = (np.sign(DF["macd"] - DF["macd_signal"]) +
                                      np.sign(DF["macd_slope"] - DF["macd_signal_slope"]))

        DF = indicators.ATR(DF, 50)
        DF = indicators.BollingerBands(DF)
        self.data.df['atr'] = DF['atr']
        self.data.df['bbands'] = DF['bbands_percent']

        self.macd_cross = self.I(lambda: self.data.df['macd_cross'], name='macd_cross')
        self.bbands_percent = self.I(lambda: DF['bbands_percent'], name='bbands_percent')
        
        #self.set_atr_periods(100)
        #self.set_trailing_sl(3)
        
    def next(self):
        price = self.data.Close[-1]
        atr = self.data.atr[-1]
        bbands_percent = self.data.bbands[-1]
        crossover = self.data.macd_cross[-1]

        pos_size = BbandMacdSystem.pos_size
        if atr > 0.2:
            if bbands_percent <= 0.6 and crossover == 2:
                self.buy(size=int(pos_size/price), tp=price+1.5*atr, sl=price-1.5*atr)
            elif bbands_percent >= 0.4 and crossover == -2:
                self.sell(size=int(pos_size/price), tp=price-1.5*atr, sl=price+1.5*atr)


from backtest.common import *
import pandas as pd

fp = "E:\Programming\Trading\Data\EBAY.USUSD_Candlestick_1_Hour_BID_07.01.2020-26.05.2021.csv"
df = pd.read_csv(fp, parse_dates = ["Local time"],
                 date_parser=lambda x: pd.to_datetime(x, utc=True, dayfirst=True))
df = dukascopy_filter(df)

data2 = df
backtest = Backtest(df, BbandMacdSystem, cash=BbandMacdSystem.cash,
                    commission=.002, hedging=True)
print(backtest.run())

backtest.plot(resample=False, filename="temp2.html")
