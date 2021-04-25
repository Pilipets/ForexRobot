from .. import FxRobot
import time
import pandas as pd

from ..data_control import FrameClient

class BaseStrategy:
    def __init__(self, robot : FxRobot, symbol,
                 update_period, bars_period, run_for : pd.Timedelta,
                 trigger_frame_size = 0, max_frame_size = 500, init_bars_cnt = 0):
        args = locals()
        del args['self']
        print('Configured BaseStrategy with', args)

        self.frame_client = FrameClient(max_frame_size)

        self.robot = robot
        self.symbol = symbol
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

    def get_trades(self):
        raise NotImplementedError('Please override get_trades in the derived class')

    def update(self, data):
        if self.frame_client.add_rows(data):
            print('Data update happened')
            
            self.frame_client.update()
            if self.trigger_frame_size <= self.frame_client.get_size():
                trigger_df = self.frame_client.get_last_bars(self.trigger_frame_size)
                
                trades = self.get_trades(trigger_df)
                robot.execute_trades(trades)

    def run(self):
        self._init_frame(self.init_bars_cnt)

        robot : FxRobot = self.robot
        run_until = time.time() + self.run_for.total_seconds()

        while time.time() < run_until:
            try:
                print("Running at ", time.time())

                data = robot.get_last_bar(self.symbol, period = self.bars_period, n = 1)
                print('Received bars:', data)

                self.update(data)
                robot.sleep_till_next_bar(data.index[-1], self.update_period)
            except KeyboardInterrupt:
                print('\nKeyboard exception received. Exiting.')
                break

        # TODO: Close all portolio opened positions.