from configparser import ConfigParser


class FxcmConfig:
    def __init__(self, access_token, server, log_level):
        self.access_token = access_token
        self.server = server
        self.log_level = log_level

    @staticmethod
    def from_file(path):
        config = ConfigParser()
        config.read(path)

        return FxcmConfig(
            access_token = config.get('Main', 'access_token'),
            server = config.get('Main', 'server'),
            log_level = config.get('Details', 'log_level')
        )

