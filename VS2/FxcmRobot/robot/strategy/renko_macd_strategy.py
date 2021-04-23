from .base_strategy import BaseStrategy
from ..data_control import FrameClient
from ..common import indicators

class RenkoMacdStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_trades(self, df):
        print('Check get_trades called with', len(df), 'items')
        #renko = indicators.renko_merge(df)