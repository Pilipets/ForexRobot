from .vectorized_strategy import VectorizedStrategy, filter_dict
from ..data_control import FrameClient
from ..common import indicators, Trade, Portfolio, TradeShortcut
import numpy as np
import pandas as pd

class BBandMacdStrategy(VectorizedStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        args = filter_dict(locals(), 'self', 'kwargs')
        self.logger.info(f'Configured {self.__class__.__name__} with {args}\n')

        for client in self.frame_clients:
            client.bbands()
            client.macd()
            client.slope('macd')
            client.slope('macd_signal')

        self.trade_pat = self.portfolio.create_trade_shortcut(
            'bbm_open', is_in_pips=True, time_in_force='GTC',
            order_type='AtMarket', trailing_step=1)

        self.close_args = self.portfolio.create_trade_shortcut(
            'bbm_close', time_in_force='GTC', order_type='AtMarket')

        self.logger.debug(f'Added new trade shortcut in Portfolio({self.portfolio.id}): {self.trade_pat}')

    def trade_signal(self, symbol, df, last_signal):
        if last_signal: return None, None

        is_buy = None
        crossover = (np.sign(df["macd"][-1] - df["macd_signal"][-1]) +
                     np.sign(df["macd_slope"][-1] - df["macd_signal_slope"][-1]))

        if df['bbands_percent'] <= 0.6 and crossover == 2: is_buy = True
        elif df['bbands_percent'] >= 0.4 and crossover == -2: is_buy = False

        if is_buy:
            self.logger.info(f'Signal[{"Buy" if is_buy else "Sell"}] found')

            amount = self.portfolio.get_lot_size(symbol)
            # TODO: Use ATR here
            trade = self.trade_pat.create_trade(
                symbol=symbol, is_buy=is_buy,amount=pos_amount, stop=-10, limit=20)
        else:
            trade = None

        return None, trade