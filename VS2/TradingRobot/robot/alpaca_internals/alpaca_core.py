from alpaca_trade_api.rest import REST, TimeFrame
from alpaca_trade_api import Stream

from .alpaca_config import AlpacaConfig

class AlpacaCore:
    def __init__(self, config : AlpacaConfig):
        self.config = config
        self.api = self._init_session(
            key_id = config.key_id,
            secret_key = config.secret_key,
            base_url = config.base_url)

    def __getattr__(self, item):
        return getattr(api, item)

    def _init_session(self, key_id, secret_key, base_url):
        return REST(key_id = key_id, secret_key=secret_key, base_url=base_url, api_version='v2')

    def create_new_stream(self):
        return Stream(self.config.key_id, self.config.secret_key, self.config.base_url)
