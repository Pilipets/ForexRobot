from .alpaca_internals import AlpacaCore, AlpacaConfig
from .common import Portfolio

import time

class TradingRobot:
    def __init__(self, config):
        self.config = config

        if type(config) == AlpacaConfig:
            self.core = AlpacaCore(config)

    def __getattr__(self, item):
        return getattr(self.core, item)
    
    def create_portfolio(self, symbols = []):
        return Portfolio(self.core, symbols)
