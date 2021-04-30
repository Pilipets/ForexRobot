from .base_strategy import BaseStrategy
from .. import FxRobot
from enum import Enum

class GridStrategy:
    class GridType(Enum):
        SYMMETRIC = 0
        BUY = 1
        SELL = 2
    SYMMETRIC_TYPE = GridType.SYMMETRIC
    BUY_TYPE = GridType.BUY
    SELL_TYPE = GridType.SELL

    def __init__(self, robot : FxRobot,
                 symbol, lower_price = 0.0, upper_price = 0.0,
                 grid_levels = 5,
                 grid_type : GridType = SYMMETRIC_TYPE, **kwargs):
        self.logger = robot.get_logger()

        args = locals(); del args['self'];
        self.logger.info(f'Configured {GridStrategy.__name__} with {args}\n')

        self.symbol = symbol
        self.robot = robot

        self.type = grid_type
        self.levels = 5
        self.lower_price = lower_price
        self.upper_price = upper_price

        self.robot.subscribe_instrument(self.symbol)
        self.interval_price = (upper_price-lower_price) / grid_levels
        self.grid = [None] * (grid_levels + 1) # n levels but n + 1 orders

        self.trade_pat = self.portfolio.create_trade_shortcut(
            'grid_pat', is_in_pips=True, time_in_force='GTC', order_type='Entry')

    def __del__(self):
        self.robot.unsubscribe_instrument(self.symbol)

    def _init_grid(self):
        robot : FxRobot = self.robot
        price = self.lower_price
        pos_amount = 10

        for i in range(len(self.grid)):
            ask_bid_price = robot.get_offers([self.symbol], ['sell', 'buy'])
            ask_price = ask_bid_price['buy']

            if  price < ask_price:
                trade = self.trade_pat.create_trade(symbol=self.symbol, is_buy=True, pos_amount=10)
                id = robot.open_trade(trade, portfolio)
            else:
                trade = self.trade_pat.create_trade(symbol=self.symbol, is_buy=False, pos_amount=10)
                id = robot.open_trade(trade, portfolio)

            self.grid[i] = id
            price += self.interval_price

    def run(self):
        pass