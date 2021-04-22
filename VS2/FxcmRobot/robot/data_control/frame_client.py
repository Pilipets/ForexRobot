import pandas as pd
from collections import defaultdict

class FrameClient:
    def __init__(self, max_size = 1000):
        self.df = pd.DataFrame()

        self.max_size = max_size
        self.indicators = {}

    def _save_strategy(self, name, func, args):
        del args['self']

        self.indicators[name] = {}
        self.indicators[name]['args'] = args
        self.indicators[name]['func'] = func

    def macd(self, fast = 12, slow = 26, macd_period = 9, name = 'macd'):
        self._save_strategy(name, self.macd, locals())
        if self.df.empty: return

        df = self.df
        df["macd_fast"]=df["close"].ewm(span=fast, min_periods=fast).mean()
        df["macd_slow"]=df["close"].ewm(span=slow, min_periods=slow).mean()
        df["macd_diff"]= df["macd_fast"] - df["macd_slow"]
        df["macd"] = df["macd_diff"].ewm(span=macd_period, min_periods=macd_period).mean()

        df.drop(['macd_fast', 'macd_slow', 'macd_diff'], axis=1, inplace=True)


    def atr(self, period = 20, name = 'atr'):
        self._save_strategy(name, self.atr, locals())
        if self.df.empty: return

        df = self.df
        df['tr_hl'] = abs(df['high'] - df['low'])
        df['tr_hp'] = abs(df['high'] - df['close'].shift(1))
        df['tr_lp'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['tr_hl', 'tr_hp', 'tr_lp']].max(axis = 1)
        df['atr'] = df['tr'].rolling(period).mean()

        df.drop(['tr_hl', 'tr_hp', 'tr_lp', 'tr'], axis=1, inplace=True)

    def boolinger_bands(self, period = 20, std = 2, name = 'bbands'):
        self._save_strategy(name, self.atr, locals())
        if self.df.empty: return

        df["bbands_ma"] = df['close'].rolling(n).mean()
        df["bbands_std"] = df["bbands_ma"].rolling(n).std()
        df["bbands_up"] = df["bbands_ma"] + std * df["bbands_std"]
        df["bbands_dn"] = df["bbands_ma"] - std * df["bbands_std"]
        df["bbands_percent"] = (df['close'] - df['bbands_dn']) / (df['bbands_up'] - df['bbands_dn'])

        df.drop(['bbands_ma', 'bbands_std', 'bbands_up', 'bbands_dn'], axis=1, inplace=True)

    def update(self):
        for indicator in self.indicators.values():
            indicator['func'](**indicator['args'])

    def get_last_bars(self, n = 1):
        return self.df.iloc[-n:]

    def add_rows(self, rows):
        i = 0
        if not df.empty:
            while i < len(rows) and self.df.index[-1] != rows.index[i]: i += 1

        if i == len(rows) or i == 0: self.df = self.df.append(rows)
        else: self.df = self.df.append(rows.iloc[i+1:])

        rows_drop = len(df) - self.max_size
        if rows_drop > 0: self.df = self.df.iloc[rows_drop:]
