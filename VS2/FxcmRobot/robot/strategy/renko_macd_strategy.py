from ..data_control import FrameClient
from .. import FxRobot
import time
import pandas as pd

class RenkoMacdStrategy:
    def __init__(self, symbol, robot : FxRobot):
        self.frame_client = FrameClient()
        self.frame_client.macd()
        self.frame_client.atr()

        self.robot = robot

        self.period = pd.Timedelta(90, unit='sec')

    def run(self):
        robot = self.robot
        for i in range(5):
            try:
                print("Running at ", time.time())
                data = robot.get_last_bar('EUR/USD', period = 'm1', n = 1)
        
                print('Received data:', data)
                self.frame_client.add_rows(data)

                self.frame_client.update()

                robot.sleep_till_next_bar(data.index[-1], self.period)
            except KeyboardInterrupt:
                print('\n\nKeyboard exception received. Exiting.')
                exit()

