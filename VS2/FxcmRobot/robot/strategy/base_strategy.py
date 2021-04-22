from .. import FxRobot
import time
import pandas as pd

from ..data_control import FrameClient

class BaseStrategy:
    def __init__(self, robot : FxRobot, symbol,
                 update_period, bars_period, run_for : pd.Timedelta,
                 init_bars_cnt = 0):
        args = locals(); del args['self']
        print('Configured BaseStrategy with', args)

        self.frame_client = FrameClient()

        self.robot = robot
        self.symbol = symbol
        self.update_period = update_period
        self.bars_period = bars_period

        self.run_for = run_for
        self.init_bars_cnt = init_bars_cnt

    def _init_frame(self, init_bars_cnt):
        if not init_bars_cnt: return

        data = self.robot.get_last_bar(
            self.symbol, period = self.bars_period, n = init_bars_cnt)
        self.frame_client.add_rows(data)

    def check_signals():
        raise NotImplementedError('Please override check_signals in the derived class')

    def run(self):
        self._init_frame(self.init_bars_cnt)
        robot : FxRobot = self.robot
        run_until = time.time() + self.run_for.total_seconds()

        while time.time() < run_until:
            try:
                print("Running at ", time.time())
                data = robot.get_last_bar('EUR/USD', period = 'm1', n = 1)
        
                print('Received bars:', data)
                if self.frame_client.add_rows(data):
                    print('Data update happened')
                    self.frame_client.update()

                    trades = self.check_signals()
                    robot.execute_trades(trades)

                robot.sleep_till_next_bar(data.index[-1], self.update_period)
            except KeyboardInterrupt:
                print('\nKeyboard exception received. Exiting.')
                break

        # TODO: Close all portolio opened positions.