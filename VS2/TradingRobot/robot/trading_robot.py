from .alpaca_internals import AlpacaCore, AlpacaConfig
from .common import Portfolio

import time

class TradingRobot:
    def __init__(self, config):
        self.config = config

        if type(config) == AlpacaConfig:
            self.core = AlpacaCore(config)
        else:
            self.core = None

    def get_core(self):
        return self.core
    
    def create_portfolio(self, symbols, pile_size, risk_rate):
        return Portfolio(self.core, symbols, pile_size, risk_rate)
