from alpaca_trade_api.rest import REST, TimeFrame

class AlpacaCore:
    def __init__(self, config):
        self.api = self._init_session(
            key_id = config.key_id,
            secret_key = config.secret_key,
            base_url = config.base_url)

    def _init_session(self, key_id, secret_key, base_url):
        return REST(key_id = key_id, secret_key=secret_key, base_url=base_url, api_version='v2')
