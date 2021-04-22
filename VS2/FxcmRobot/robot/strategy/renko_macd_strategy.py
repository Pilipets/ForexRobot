from .base_strategy import BaseStrategy

class RenkoMacdStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_client.macd()
        self.frame_client.atr()

    def check_signals(self):
        print('Check signals called')
        pass

