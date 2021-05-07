from .vectorized_strategy import VectorizedStrategy, filter_dict
from ..data_control import FrameClient
from ..common import indicators, Trade, Portfolio, TradeShortcut
import numpy as np
import pandas as pd

class RenkoMacdStrategy(VectorizedStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        args = filter_dict(locals(), 'self', 'kwargs')
        self.logger.info(f'Configured {self.__class__.__name__} with {args}\n')

        self.pos_amount = 10
        self.close_args = dict(time_in_force='GTC', order_type='AtMarket', amount=self.pos_amount)
        self.trade_pat = self.portfolio.create_trade_shortcut(
            'rm_pat', is_in_pips=True, time_in_force='GTC',
            order_type='AtMarket', trailing_step=1)

        self.logger.debug(f'Added new trade shortcut in Portfolio({self.portfolio.id}): {self.trade_pat}')

    def prepare_df(self, df):
        renko_df = indicators.RenkoDF(df) # df index is reset in the RenkoDF
        df = df.merge(renko_df.loc[:,["date", "bar_num"]], how="outer", on="date")

        df["bar_num"].fillna(method = 'ffill', inplace = True)
        df.set_index('date', inplace=True)

        client = FrameClient.from_df(df)
        client.macd()
        client.atr()
        client.slope('macd')
        client.slope('macd_signal')

        return client.get_df().dropna()

    def trade_signal(self, df, last_signal):
        close, signal = False, None
        bar_num = df["bar_num"][-1]
        crossover = (np.sign(df["macd"][-1] - df["macd_signal"][-1]) +
            np.sign(df["macd_slope"][-1] - df["macd_signal_slope"][-1]))

        if last_signal is None:
            if bar_num >= 2 and crossover == 2: signal = "Buy"
            elif bar_num <= -2 and crossover == -2: signal = "Sell"
            
        elif last_signal == "long":
            if bar_num <= -2 and crossover == -2: close, signal = True, "Sell"
            elif crossover == -2: close = True
            
        elif last_signal == "short":
            if bar_num >= 2 and crossover == 2: close, signal = True, "Buy"
            elif crossover == 2: close = True

        if close or signal: self.logger.info(f'Close[{close}], Signal[{signal}] found')
        return close, signal