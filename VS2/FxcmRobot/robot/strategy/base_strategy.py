from .. import FxRobot
import time
import pandas as pd

from ..data_control import FrameClient

class BaseStrategy:
    def __init__(self, robot, update_period):
        self.frame_client = FrameClient()
        self.robot = robot
        self.update_period = update_period

    def check_signals():
        pass

    def run(self):
        robot = self.robot
        for i in range(3):
            try:
                print("Running at ", time.time())
                data = robot.get_last_bar('EUR/USD', period = 'm1', n = 1)
        
                print('Received data:', data)
                self.frame_client.add_rows(data)
                self.frame_client.update()

                trades = self.check_signals()
                robot.execute_trades(trades)

                robot.sleep_till_next_bar(data.index[-1], self.update_period)
            except KeyboardInterrupt:
                print('\n\nKeyboard exception received. Exiting.')
                exit()