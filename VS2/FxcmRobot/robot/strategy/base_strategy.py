import time
import pandas as pd

from fxcmpy import fxcmpy_open_position
from .. import FxRobot
from ..common import Portfolio

def filter_dict(map, *args):
    for x in args:
        del map[x]
    return map

class BaseStrategy:
    def __init__(self, robot : FxRobot, portfolio : Portfolio, run_for : pd.Timedelta):
        args = filter_dict(locals(), 'self')
        args['portfolio'] = portfolio.id

        self.robot = robot
        self.logger = self.robot.get_logger()
        self.logger.info(f'Configured {self.__class__.__name__} with {args}\n')

        self.symbols = list(portfolio.get_symbols())
        self.portfolio = portfolio
        self.run_for = run_for

        for symbol in self.symbols:
            self.robot.subscribe_instrument(symbol)

    def __del__(self):
        for symbol in self.symbols:
            self.robot.unsubscribe_instrument(symbol)

    def _group_porfolio_positions(self):
        data = self.robot.get_open_positions()
        if data.empty: return data.groupby([])

        grouped = data.loc[(data['currency'].isin(self.portfolio.get_symbols()))
                           & (data['orderId'].isin(self.portfolio.get_order_ids())),
                           ['currency', 'isBuy', 'tradeId', 'orderId','amountK']]
        return grouped.groupby(['currency'])

    def _clean_portfolio_positions(self, attempts=3):
        ids = self.portfolio.get_order_ids()
        self.logger.info(f'Cleaning {len(ids)} portfolio({self.portfolio.id}) orders with {attempts} attempts')
        for id in self.portfolio.get_order_ids():
            for _ in range(attempts):
                try:
                    id = int(id)
                    order = self.robot.get_order(id)
                    self.logger.info(f"Closing order({id}) with status({order.get_status()})")
                    order.delete()

                except Exception as ex:
                    self.logger.warning(f'Exception received: {ex}')

                else:
                    break

    def start_run(self):
        pass

    def iter_run(self):
        pass

    def end_run(self):
        self._clean_portfolio_positions()

    def run(self):
        self.start_run()

        robot : FxRobot = self.robot
        run_until = time.time() + self.run_for.total_seconds()
        self.logger.info(f'Running strategy until {pd.Timestamp.now() + self.run_for}\n')

        while time.time() < run_until:
            try:
                self.logger.info(f'Running iteration at {pd.Timestamp.utcnow()}')
                self.iter_run()

            except KeyboardInterrupt:
                self.logger.error('Keyboard exception received. Exiting.\n')
                break

            except Exception as ex:
                self.logger.error(f'\nUnhandled exception received: {ex}\n')
                break

        self.end_run()