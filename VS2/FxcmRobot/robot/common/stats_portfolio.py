from .base_portfolio import BasePortfolio
import pandas as pd
import numpy as np

class StatsPortfolio(BasePortfolio):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def max_drawdown(self, df, col='cum_res'):
        drawdown = 1 - df[col] / df[col].cummax()
        return drawdown.max()

    def get_closed_positions(self):
        pos = self.robot.get_closed_positions()
        return pos[pos['OpenOrderID'].isin(self.order_ids)]
        
    def get_stats(self, granularity = 1):
        pos = self.get_closed_positions()

        trades_cnt = len(pos)
        profits = []
        losses = []
        if not pos.empty:
            pos['openTime'] = pos['openTime'].astype('int64')
            pos['closeTime'] = pos['closeTime'].astype('int64')
            pos.sort_values('closeTime', inplace=True)
            pos['cumProfit'] = pos['grossPL'].cumsum()

            for income in pos['grossPL']:
                if income > 0: profits.append(income)
                else: losses.append(income)

        print('STRATEGY PERFORMANCE'.center(40, '*'))
        print('-'*40)
        print('Maximum drawdown', round(self.max_drawdown(pos, 'cumProfit') * 100, 2), '% \n')

        print('Number of trades/profits/losses:', trades_cnt, '/', len(profits), '/', len(losses))
        print('Win/loss ratio:', round(len(profits) / max(len(losses), 1), 2))
        print('Batting average:', round((len(profits) / max(trades_cnt, 1)) * 100, 2), '%')
        print('ROI:', round(pos['cumProfit'].iloc[-1], 2) if not pos.empty else 0, '$')

        print('-'*40)
        print('Average profitable/lossing trade:',
              round(np.mean(profits), 2) if profits else 0, '$ /',  round(np.mean(losses), 2) if losses else 0, '$')
        print('Max profitable/lossing trade:',
              round(max(profits), 2) if profits else 0, '$ /', round(min(losses), 2) if losses else 0, '$')