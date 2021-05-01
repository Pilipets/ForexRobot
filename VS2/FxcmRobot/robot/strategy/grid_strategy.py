from enum import Enum

from .base_strategy import BaseStrategy
from .. import FxRobot

class GridStrategy(BaseStrategy):
    class GridType(Enum):
        SYMMETRIC = 0
        BUY = 1
        SELL = 2
    SYMMETRIC_TYPE = GridType.SYMMETRIC
    BUY_TYPE = GridType.BUY
    SELL_TYPE = GridType.SELL

    def __init__(self, lower_price = 0.0, upper_price = 0.0,
                 grid_levels = 5, moving_grid = False,
                 grid_type : GridType = SYMMETRIC_TYPE, **kwargs):
        super().__init__(**kwargs)

        args = locals(); del args['self']; del args['kwargs']
        self.logger.info(f'Configured {GridStrategy.__name__} with {args}')

        self.symbol = self.portfolio.get_symbols()[0]

        self.type = grid_type
        self.levels = grid_levels
        self.lower_price = lower_price
        self.upper_price = upper_price

        self.robot.subscribe_instrument(self.symbol)
        self.interval_price = (upper_price-lower_price) / grid_levels
        self.grid = [None] * (grid_levels + 1) # n levels but n + 1 orders

        self.trade_pat = self.portfolio.create_trade_shortcut(
            'grid_pat', is_in_pips=True, time_in_force='GTC', order_type='Entry')

        self.logger.debug(f'Added new trade shortcut in Portfolio({portfolio.id}): {self.trade_pat}')

    def __del__(self):
        self.robot.unsubscribe_instrument(self.symbol)

    def start_run(self):
        robot : FxRobot = self.robot
        pos_amount = 10

        price = self.lower_price
        for i in range(len(self.grid)):
            ask_price = robot.get_offers([self.symbol], ['buy'])['buy']

            if  price < ask_price:
                trade = self.trade_pat.create_trade(
                    symbol=self.symbol, is_buy=True,
                    limit=price, amount=pos_amount)
                id = robot.open_trade(trade, portfolio)
            else:
                trade = self.trade_pat.create_trade(
                    symbol=self.symbol, is_buy=False,
                    limit=price, amount=pos_amount)
                id = robot.open_trade(trade, portfolio)

            self.grid[i] = id
            price += self.interval_price

    def iter_run(self):
        pos_amount = 10
        
        for idx, id in enumerate(self.grid):
            order = robot.get_order(id) if id else None
            status = order.get_status() if order else None

            if status == "Executed":
                grid[idx] = None
                side = "Buy" if order.get_isBuy() else "Sell"
                msg = f'{side} order({id}) completed, setting new '

                old_price = order.get_limit()
                if order.get_isBuy():
                    new_price = old_price + self.interval_price
                    trade = self.trade_pat.create_trade(
                        symbol=self.symbol, is_buy=False,
                        limit=new_price, amount=pos_amount
                    )
                    msg += 'Sell order'

                else:
                    new_price = old_price - self.interval_price
                    trade = self.trade_pat.create_trade(
                        symbol=self.symbol, is_buy=True,
                        limit=new_price, amount=pos_amount
                    )
                    msg += 'Buy order'

                id = robot.open_trade(trade, portfolio)
                grid[idx] = id

                self.logger.info(msg)

            elif status == "Canceled" or status is None:
                pass