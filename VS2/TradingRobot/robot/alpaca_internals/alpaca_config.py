from configparser import ConfigParser


class AlpacaConfig:
    def __init__(self, key_id, secret_key, base_url, timezone):
        self.key_id = key_id
        self.secret_key = secret_key
        self.base_url = base_url
        self.timezone = timezone

    @staticmethod
    def from_file(path):
        config = ConfigParser()
        config.read(path)

        return AlpacaConfig(
            key_id = config.get('Alpaca', 'key_id'),
            secret_key = config.get('Alpaca', 'secret_key'),
            base_url = config.get('Alpaca', 'base_url'),
            timezone = config.get('Details', 'timezone')
        )
