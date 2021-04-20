from alpaca_trade_api.rest import REST, TimeFrame
from alpaca_trade_api import Stream

from .alpaca_config import AlpacaConfig
import pandas as pd

class AlpacaCore:
    def __init__(self, config : AlpacaConfig):
        self.config = config
        self.api = self.create_new_api(config.key_id, config.secret_key, config.base_url)

    def now(self):
        return pd.Timestamp.now(tz = self.config.timezone)

    def is_market_open(self):
        return self.api.get_clock().is_open

    def create_new_api(self, key_id, secret_key, base_url):
        return REST(key_id = key_id, secret_key=secret_key, base_url=base_url, api_version='v2')

    def get_api(self):
        return self.api

    def create_new_stream(self):
        return Stream(self.config.key_id, self.config.secret_key, self.config.base_url)
