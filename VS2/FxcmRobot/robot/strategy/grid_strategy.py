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
                 grid_levels = 5, moving_grid = False,
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

    def run(self):
        robot : FxRobot = self.robot
        run_until = time.time() + self.run_for.total_seconds()
        self.logger.info(f'Running strategy until {pd.Timestamp.now() + self.run_for}\n')

        pos_amount = 10
        while time.time() < run_until:
            try:
                self.logger.info(f'Running iteration at {pd.Timestamp.utcnow()}')

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

                self.logger.info('\n')

            except KeyboardInterrupt:
                self.logger.error('Keyboard exception received. Exiting.\n')
                break

            except Exception as ex:
                self.logger.error(f'\nUnhandled exception received: {ex}\n')
                break