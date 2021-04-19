from .internals import AlpacaCore
import time

class AlpacaBot:
    def __init__(self, config):
        self.config = config
        self.core = AlpacaCore(config)

    def __getattr__(self, item):
        return getattr(self.api, item)
    
    def create_portfolio():
        return Portfolio(self.core)

    def run(self, portfolio, period):
        starttime = time.time()
        while True:
            portfolio.update()
            time.sleep(period - ((time.time() - starttime) % period))
