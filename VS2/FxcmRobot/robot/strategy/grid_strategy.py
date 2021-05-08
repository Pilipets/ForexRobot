from enum import Enum

from .base_strategy import BaseStrategy, filter_dict
from .. import FxRobot
from itertools import chain
import pandas as pd

class GridStrategy(BaseStrategy):
    def __init__(self, update_period : pd.Timedelta = None,
                 lower_price = None, upper_price = None,
                 interval_price = None, base_price = None,
                 grid_levels = 5, moving_grid = False,
                 **kwargs):
        super().__init__(**kwargs)

        self.symbol = next(iter(self.portfolio.get_symbols()))

        self.lower_price = lower_price
        self.upper_price = upper_price
        self.levels = grid_levels + 1

        self.pos_amount = self.portfolio.get_lot_size(self.symbol)

        if update_period is None: update_period = pd.Timedelta(10, 'sec')
        self.update_period = update_period

        if upper_price and lower_price:
            if interval_price is None:
                interval_price = (upper_price-lower_price) / grid_levels
            if not moving_grid and base_price is None:
                base_price = interval_price * (self.levels // 2) + lower_price

        args = filter_dict(locals(), 'self', 'kwargs')
        self.logger.info(f'Configured {self.__class__.__name__} with {args}\n')

        self.interval_price = interval_price
        self.base_price = base_price
        self.grid = [None] * self.levels

        self.trade_pat = self.portfolio.create_trade_shortcut(
            'grid_pat', symbol = self.symbol, is_in_pips=True,
            time_in_force='GTC', order_type='Entry')

        self.logger.debug(f'Added new trade shortcut in Portfolio({self.portfolio.id}): {self.trade_pat}')

    def _fill_level(self, level, is_buy):
        robot : FxRobot = self.robot

        if 0 <= level <= self.levels and self.grid[level] is None:
            price = self.base_price  + self.interval_price * (level - self.levels // 2)

            try:
                trade = self.trade_pat.create_trade(
                    is_buy=is_buy, rate=price, amount=self.pos_amount)
        
                self.grid[level] = robot.open_trade(trade, self.portfolio)

            except Exception as ex:
                self.logger.warning(f'Exception received when filling the level({level}): {ex}')
                self.grid[level] = None

    def start_run(self):
        self.logger.info(f'Starting the {self.__class__.__name__} strategy')
        super().start_run()

        if self.base_price is None:
            self.base_price = self.robot.get_offers(self.symbol, 'buy')['buy'].iloc[0]
        if self.interval_price is None:
            # Use ATR or BoolingerBands to deduce the interval_price
            pass

        self.last_level = self.levels // 2
        self.grid = [None] * self.levels

        # Half buy, half sell
        for level in range(self.last_level - 1, -1, -1):
            self._fill_level(level, is_buy=True)
        for level in range(self.last_level + 1, len(self.grid)):
            self._fill_level(level, is_buy=False)

    def iter_run(self):
        robot : FxRobot = self.robot
        grid = self.grid

        # https://github.com/fxcm/RestAPI/issues/138
        for level in chain(range(self.last_level + 1, len(grid)), range(self.last_level - 1, -1, -1)):
            order = robot.get_order(grid[level]) if grid[level] else None

            if not order or order.get_status() == "Canceled":
                grid[level] = None
                if level > self.last_level: self._fill_level(level, is_buy=False)
                elif level < self.last_level: self._fill_level(level, is_buy=True)

            elif order.get_status() == "Executed":
                self.last_level = level
                grid[level] = None

                offer_price = robot.get_offers(self.symbol, ['sell', 'buy']).iloc[0]
                if order.get_isBuy():
                    if order.get_buy() < offer_price['sell']: self._fill_level(level+1, is_buy=False)
                    else: self._fill_level(level, is_buy=True)
                else:
                    if order.get_sell() > offer_price['buy']: self._fill_level(level-1, is_buy=True)
                    else: self._fill_level(level, is_buy=False)

        self.robot.sleep_till_next_bar(None, self.update_period)

    def end_run(self):
        self.logger.info(f'Finishing the {self.__class__.__name__} strategy')
        super().end_run()