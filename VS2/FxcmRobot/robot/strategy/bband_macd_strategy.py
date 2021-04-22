from .base_strategy import BaseStrategy

class RenkoMacdStrategy(BaseStrategy):
    def __init__(self, symbol, robot, update_period):
        super().__init__(robot, update_period)

        self.frame_client.macd()
        self.frame_client.atr()

    def check_signals(self):
        print('Check signals called')
        pass


