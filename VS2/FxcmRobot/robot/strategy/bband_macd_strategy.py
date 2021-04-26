from .base_strategy import BaseStrategy

class BbandMacdStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_client.macd()
        self.frame_client.bbands()

    def check_signals(self):
        print('Check signals called')
        pass