from .base_strategy import BaseStrategy
from ..data_control import FrameClient

class RenkoMacdStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def check_signals(self):
        print('Check signals called')

        bars = self.frame_client.get_last_bars(self.signal_frame_size).dropna()
        client = FrameClient.from_df(self.trigger_frame_size, )
        bars = self.frame_client.get_last_bars(self.signal_frame_size).dropna()