from configparser import ConfigParser

class FxcmConfig:
    def __init__(self, access_token, server, log_level):
        self.access_token = access_token
        self.server = server
        self.log_level = log_level

    def __repr__(self):
        return f'{FxcmConfig.__name__}({self.__dict__})'

class FxConfig:
    def __init__(self, log_level, fxcm_config):
        self.log_level = log_level
        self.fxcm_config = fxcm_config 

    @staticmethod
    def from_file(file_path):
        config = ConfigParser()
        config.read(file_path)

        return FxConfig(
            config.get('Robot', 'log_level'),
            FxcmConfig(
                access_token=config.get('Fxcm', 'access_token'),
                server=config.get('Fxcm', 'server'),
                log_level=config.get('Fxcm', 'log_level')
            )
        )

    def __repr__(self):
        return f'{FxConfig.__name__}({self.__dict__})'