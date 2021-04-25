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

        self.frame_client = FrameClient(max_frame_size)

        self.robot = robot
        self.symbols = portfolio.get_symbols()
        self.portfolio = portfolio
        self.update_bars_cnt = update_bars_cnt
        self.update_period = update_period
        self.bars_period = bars_period

        self.run_for = run_for
        self.trigger_frame_size = trigger_frame_size
        self.init_bars_cnt = init_bars_cnt

    def _init_frame(self, init_bars_cnt):
        if not init_bars_cnt: return

        data = self.robot.get_last_bar(
            self.symbol, period = self.bars_period, n = init_bars_cnt)
        self.frame_client.add_rows(data)

    def update_trades(self):
        raise NotImplementedError('Please override update_trades in the derived class')

    def run(self):
        self._init_frame(self.init_bars_cnt)

        robot : FxRobot = self.robot
        run_until = time.time() + self.run_for.total_seconds()

        while time.time() < run_until:
            try:
                print("Running at ", time.time())

                data = robot.get_last_bar(
                    self.symbol, period = self.bars_period, n = self.update_bars_cnt)
                print('Received bars:', data)

                if self.frame_client.add_rows(data):
                    print('Data update happened')
            
                    self.frame_client.update()
                    if self.trigger_frame_size <= self.frame_client.get_size():
                        trigger_df = self.frame_client.get_last_bars(self.trigger_frame_size)
                        self.update_trades(trigger_df)

                robot.sleep_till_next_bar(data.index[-1], self.update_period)
            except KeyboardInterrupt:
                print('\nKeyboard exception received. Exiting.')
                break

        # TODO: Close all portolio opened positions.