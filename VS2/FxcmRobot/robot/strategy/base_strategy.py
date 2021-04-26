from .. import FxRobot
import time
import pandas as pd

from ..data_control import FrameClient
from ..common import Portfolio

class BaseStrategy:
    def __init__(self, robot : FxRobot, portfolio : Portfolio,
                 update_period, bars_period, run_for : pd.Timedelta,
                 update_bars_cnt = 1, trigger_frame_size = 0, max_frame_size = 500,
                 init_bars_cnt = 0):
        args = locals(); del args['self']; del args['portfolio'];

        self.robot = robot
        self.logger = self.robot.get_logger()
        self.logger.info(f'Configured {BaseStrategy.__name__} with {args}')

        self.symbols = list(portfolio.get_symbols())
        self.frame_clients = [FrameClient(max_frame_size)
                              for _ in range(len(self.symbols))]
        self.portfolio = portfolio

        self.update_bars_cnt = update_bars_cnt
        self.update_period = update_period
        self.bars_period = bars_period
        self.run_for = run_for
        self.trigger_frame_size = trigger_frame_size
        self.init_bars_cnt = init_bars_cnt

    def _init_frame(self, init_bars_cnt):
        if not init_bars_cnt: return

        for idx, symbol in enumerate(self.symbols):
            try:
                self.logger.debug(f'Initializing {symbol} frame with {init_bars_cnt} elements')
                data = self.robot.get_last_bar(symbol,
                                               period = self.bars_period,
                                               n = init_bars_cnt)
                self.frame_clients[idx].add_rows(data)
            except Exception as ex:
                print(ex)

    def update_trades(self):
        raise NotImplementedError('Please override update_trades in the derived class')

    def run(self):
        self._init_frame(self.init_bars_cnt)

        robot : FxRobot = self.robot
        run_until = time.time() + self.run_for.total_seconds()
        self.logger.info(f'Running strategy until {pd.Timestamp.now() + self.run_for}')

        while time.time() < run_until:
            try:
                last_bar_time = pd.Timestamp.now()
                self.logger.info(f'Running iteration at {last_bar_time}')

                df_updates = [(pd.DataFrame(), False) for _ in range(len(self.symbols))]
                for idx, symbol in enumerate(self.symbols):
                    try:
                        self.logger.info(f'Processing {symbol} update')
                        data = robot.get_last_bar(symbol, period = self.bars_period,
                                                  n = self.update_bars_cnt)
                        last_bar_time = data.index[-1]

                        client = self.frame_clients[idx]
                        if client.add_rows(data):
                            self.logger.debug(f'Data update happened for {symbol}')
            
                            if self.trigger_frame_size <= client.get_size():
                                trigger_df = client.get_last_bars(self.trigger_frame_size)
                                df_updates[idx] = trigger_df, True

                    except Exception as ex:
                        self.logger.warning(f'Exception received: {ex}')

                self.update_trades(df_updates)
                robot.sleep_till_next_bar(last_bar_time, self.update_period)

            except KeyboardInterrupt:
                self.logger.error('\nKeyboard exception received. Exiting.')
                break

            except Exception as ex:
                self.logger.error(f'\nUnhandled exception received: {ex}')
                break