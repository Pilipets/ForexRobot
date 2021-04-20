from .alpaca_internals import AlpacaCore
from .common import Portfolio

import time

class TradingRobot:
    def __init__(self, config):
        self.config = config
        self.core = AlpacaCore(config)

    def __getattr__(self, item):
        return getattr(self.core, item)
    
    def create_portfolio(self, symbols = []):
        return Portfolio(self.core, symbols)

    def run(self, portfolio, period):
        raise NotImplementedError("Run isn't implemented yet")
        starttime = time.time()
        while True:
            portfolio.update()
            time.sleep(period - ((time.time() - starttime) % period))
