from datetime import timedelta

from backtesting import Trade, StatsBackTestSimulator
from tech_indicators import renko_DF, MACD, slope, ATR
import numpy as np

# Combination of Renko bricks and MACD
class RenkoMACDSimulator(StatsBackTestSimulator):
    def __init__(self, ticker, df, **params):
        super().__init__(ticker, df, **params)
        
    def _process_df(self, renko_brick_size = 0.5, atr_period = 120,
                    macd_a = 12, macd_b = 26, macd_c = 9, slope_period = 5):
        data = self.df

        renko = renko_DF(data, atr_period, renko_brick_size)
        data.reset_index(inplace=True)

        data_renko = data.merge(renko.loc[:,["Date", "bar_num"]], how="outer", on="Date")

        data_renko["bar_num"].fillna(method = 'ffill', inplace = True)
        data_renko = MACD(data_renko, macd_a, macd_b, macd_c)

        data_renko["MACD_slope"] = slope(data_renko["MACD"], 5)
        data_renko["MACD_sig_slope"] = slope(data_renko["MACD_sig"], 5)
        data_renko["ATR"] = ATR(data_renko, atr_period)
        data_renko.dropna(inplace = True)
        data_renko.set_index('Date', inplace = True)

        self.df = data_renko

    def test_strategy(self, open_limit, balance, ATR_SL = 0.5, risk_rate = 0.05):
        # Initialize testing
        super()._reset_trades(balance, risk_rate)

        df = self.df
        for i in range(len(self.df) - 1):
            cur_price = df['Close'][i]

            crossover = np.sign(df["MACD"][i] - df["MACD_sig"][i]) + np.sign(df["MACD_slope"][i] - df["MACD_sig_slope"][i])
            # Enter trades---------------------------------------------------------------------------
            # 1. Buy
            if len(self.open_trades) < open_limit and df["bar_num"][i] >= 2 and crossover == 2:
                take_profit, stop_loss = df['ATR'][i] * 2 * ATR_SL, -df['ATR'][i] * ATR_SL

                self.set_new_trade(i, type = Trade.Type.LONG, entry_price = cur_price,
                                   take_profit = take_profit, stop_loss = stop_loss)
            
            # 2. Sell
            if len(self.open_trades) < open_limit and df["bar_num"][i] <= -2 and crossover == -2:

                take_profit, stop_loss = -df['ATR'][i] * 2 * ATR_SL, df['ATR'][i] * ATR_SL

                self.set_new_trade(i, type = Trade.Type.SHORT, entry_price = cur_price,
                                   take_profit = take_profit, stop_loss = stop_loss)

            # Exit profit or stop loss trades---------------------------------------------------------------
            self.safe_exit_trades(i)

            # Exit after MACD crossover-----------------------------------------------------------------
            if crossover != 0:
                self.force_exit_trades(i, lambda x: (x.is_long() and crossover == -2) or (x.is_short() and crossover == 2))


        # Force exit on all trades---------------------------------------------------------------------
        self.force_exit_trades(i+1, lambda x: True)
