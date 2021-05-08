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

        self.close_args = dict(time_in_force='GTC', order_type='AtMarket')
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

    def trade_signal(self, symbol, df, last_signal):
        close, is_buy = False, None

        bar_num = df["bar_num"][-1]
        crossover = (np.sign(df["macd"][-1] - df["macd_signal"][-1]) +
            np.sign(df["macd_slope"][-1] - df["macd_signal_slope"][-1]))

        if last_signal is None:
            if bar_num >= 2 and crossover == 2: is_buy = True
            elif bar_num <= -2 and crossover == -2: is_buy = False
            
        elif last_signal == "long":
            if bar_num <= -2 and crossover == -2: close, is_buy = True, False
            elif crossover == -2: close = True
            
        elif last_signal == "short":
            if bar_num >= 2 and crossover == 2: close, is_buy = True, True
            elif crossover == 2: close = True

        trade = None
        if close or is_buy:
            self.logger.info(f'Close[{close}], Signal[{"Buy" if is_buy else "Sell"}] found')
            if close:
                close = self.close_args
                close['amount'] = self.portfolio.get_lot_size(symbol)

            if is_buy:
                amount = self.portfolio.get_lot_size(symbol)
                trade = self.trade_pat(
                    symbol=symbol, is_buy=is_buy,amount=pos_amount, stop=-10)

        return close, trade