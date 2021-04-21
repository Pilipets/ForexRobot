import pandas as pd
from collections import defaultdict

class FrameClient:
    def __init__(self):
        self.df = pd.DataFrame()

        self.indicators = {}

    def _save_strategy(self, name, func, args):
        del args['self']

        self.indicators[name] = {}
        self.indicators[name]['args'] = args
        self.indicators[name]['func'] = func

    def macd(self, fast = 12, slow = 26, macd_period = 9, name = 'macd'):
        self._save_strategy(name, self.macd, locals())

        df = self.df
        df["macd_fast"]=df["close"].ewm(span=fast, min_periods=fast).mean()
        df["macd_slow"]=df["close"].ewm(span=slow, min_periods=slow).mean()
        df["macd_diff"]= df["macd_fast"] - df["macd_slow"]
        df["macd"] = df["macd_diff"].ewm(span=macd_period, min_periods=macd_period).mean()

        df.drop(labels=['macd_fast', 'macd_slow', 'macd_diff'], axis=1, inplace=True)


    def atr(self, period = 20, name = 'atr'):
        self._save_strategy(name, self.atr, locals())

        df = self.df
        df['tr_hl'] = abs(df['high'] - df['low'])
        df['tr_hp'] = abs(df['high'] - df['close'].shift(1))
        df['tr_lp'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['tr_hl', 'tr_hp', 'tr_lp']].max(axis = 1)
        df['atr'] = df['tr'].rolling(period).mean()

        df.drop(labels=['tr_hl', 'tr_hp', 'tr_lp', 'tr'], axis=1, inplace=True)

    def update(self):
        for indicator in self.indicators.values():
            indicator['func'](**indicator['args'])

    def get_last_bars(self, n = 1):
        return self.df[-n]

    def add_rows(self, rows):
        pass
