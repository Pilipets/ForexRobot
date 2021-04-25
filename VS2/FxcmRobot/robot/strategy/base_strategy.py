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
        args = locals()
        del args['self']
        print('Configured BaseStrategy with', args)

        self.robot = robot
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
                print('Initializing', symbol, 'frame with', init_bars_cnt, 'elements')
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

        while time.time() < run_until:
            try:
                print("Running at ", time.time())

                last_bar_time = pd.Timestamp.now()
                df_updates = [(pd.DataFrame(), False) for _ in range(len(self.symbols))]

                for idx, symbol in enumerate(self.symbols):
                    try:
                        data = robot.get_last_bar(symbol, period = self.bars_period,
                                                  n = self.update_bars_cnt)

                        print('Received bars for', symbol, ':', data)
                        last_bar_time = min(last_bar_time, data.index[-1])

                        client = self.frame_clients[idx]
                        if client.add_rows(data):
                            print('Data update happened for', symbol)
            
                            if self.trigger_frame_size <= client.get_size():
                                trigger_df = client.get_last_bars(self.trigger_frame_size)
                                df_updates[idx] = trigger_df, True

                    except Exception as ex:
                        print("Exception received when getting the data update for", symbol)
                        print(ex)

                self.update_trades(df_updates)
                robot.sleep_till_next_bar(last_bar_time, self.update_period)
            except KeyboardInterrupt:
                print('\nKeyboard exception received. Exiting.')
                break