from ..data_control import FrameClient

class RenkoMacdStrategy:
    def __init__(self, symbol):
        self.symbol = symbol

        self.frame_client = FrameClient()