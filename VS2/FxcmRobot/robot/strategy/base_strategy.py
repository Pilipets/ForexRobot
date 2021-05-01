import time
import pandas as pd

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

    def start_run(self):
        pass

    def iter_run(self):
        pass

    def end_run(self):
        pass

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