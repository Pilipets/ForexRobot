import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from .base_simulator import BackTestSimulator

class StatsBackTestSimulator(BackTestSimulator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.res_df = pd.DataFrame()

    def CAGR(self, df, granularity = 1):
        if df['cum_res'][-1] < 0: return np.nan

        n = len(self.df) / (252*granularity) # number of years
        return (((df['cum_res'][-1] / self.initial_balance)**(1/n)) - 1)

    # 1 - good, 2 - very good, 3 - excellent, risk free rate in USA is 0.022
    def sharpe_ratio(self, df, granularity = 1, rf = 0.022):
        returns = df['cum_res'].pct_change()
        volatility = returns.std() * np.sqrt(252 * granularity)
        return (self.CAGR(df, granularity) - rf) / volatility

    def max_drawdown(self, df):
        drawdown = 1 - df['cum_res'] / df['cum_res'].cummax()
        return drawdown.max()

    def plot(self, name):
        if self.res_df is None: return
        ax = self.res_df['cum_res'].plot(title = f'{name}({self.ticker})')
        ax.set_xlabel("Date")
        ax.set_ylabel("Balance")
        plt.show()

    def get_stats(self, granularity = 1):
        if not self.closed_trades:
            self.res_df = None
            return

        res_df = pd.DataFrame([{'result': t.result, 'date': t.date} for t in self.closed_trades])
        res_df.set_index('date', inplace= True)
        res_df.sort_index(inplace = True)

        res_df['cum_res'] = res_df['result'].cumsum() + self.initial_balance


        profits = []
        losses = []
        for t in self.closed_trades:
            if t.result > 0.1: profits.append(t.result)
            else: losses.append(t.result)

        print('***** STRATEGY PERFORMANCE *****')
        print('--------------------------------')
        print('CAGR:', round(self.CAGR(res_df, granularity) * 100, 2), '%')
        print('Sharpe ratio:', round(self.sharpe_ratio(res_df, granularity), 2))
        print('Maximum drawdown', round(self.max_drawdown(res_df) * 100, 2), '% \n')

        print('Number of trades/profits/losses:', len(self.closed_trades), '/', len(profits), '/', len(losses))
        print('Win/loss ratio:', (round(len(profits) / max(len(losses), 1), 2)))
        print('Batting average:', (round(len(profits) / (len(self.closed_trades)) * 100, 2)), '%')
        print('ROI:', round(res_df['cum_res'][-1]) - self.initial_balance)
        print('Net performance:', round ((self.balance - self.initial_balance) / self.initial_balance * 100, 2), '%')

        print('--------------------------------')
        print('Average profitable/lossing trade:', round(np.mean(profits) if profits else 0, 2), '/', round(np.mean(losses) if losses else 0, 2))
        print('Max profitable/lossing trade:', round(max(profits) if profits else 0, 2), '/', round(min(losses) if losses else 0, 2))
        print('Max lossing trade:', round(min(losses) if losses else 0, 2))

        self.res_df = res_df