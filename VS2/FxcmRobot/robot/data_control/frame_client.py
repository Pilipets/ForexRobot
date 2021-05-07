import pandas as pd
from collections import OrderedDict

from ..common import indicators

class FrameClient:
    def __init__(self, max_size):
        self.df = pd.DataFrame()

        self.max_size = max_size
        self.indicators = OrderedDict()

    @staticmethod
    def from_df(df):
        client = FrameClient(len(df))
        client.df = df
        return client

    def get_df(self):
        return self.df

    def _save_indicator(self, name, func, args):
        del args['self']

        self.indicators[name] = {'args': args, 'func': func}
        return not self.df.empty

    def macd(self, fast = 12, slow = 26, macd_period = 9, name = 'macd'):
        if not self._save_indicator(name, self.macd, locals()): return
        self.df = indicators.MACD(self.df, fast = fast, slow = slow, macd_period = macd_period)

    def atr(self, period = 20, name = 'atr'):
        if not self._save_indicator(name, self.atr, locals()): return
        self.df = indicators.ATR(self.df, period = period)

    def bbands(self, period = 20, up_std = 2, dn_std = 2, name = 'bbands'):
        if not self._save_indicator(name, self.bbands, locals()): return
        self.df = indicators.BollingerBands(self.df, period = period, up_std = up_std, dn_std = dn_std)

    def slope(self, col_name, num = 5, name= 'slope'):
        if not self._save_indicator(name, self.slope, locals()): return
        self.df[f'{col_name}_slope'] = indicators.slope(self.df.loc[:, col_name], num)

    def update(self):
        for indicator in self.indicators.values():
            indicator['func'](**indicator['args'])

        rows_drop = len(self.df) - self.max_size
        if rows_drop > 0: self.df = self.df.iloc[rows_drop:]

    def get_last_bars(self, n = 1):
        return self.df.iloc[-n:]

    def get_size(self):
        return len(self.df)

    def add_rows(self, rows):
        if rows.empty: return False
        elif self.df.empty:
            self.df = self.df.append(rows)
            changed = True
        else:
            i = 0
            while i < len(rows) and self.df.index[-1] != rows.index[i]: i += 1

            if i == len(rows): self.df = self.df.append(rows)
            else: self.df = self.df.append(rows.iloc[i+1:])
            changed = (i == len(rows) or i + 1 != len(rows))

        return changed