
class FxcmBot:
    def __init__(self, config):
        self.config = config

        if type(config) == AlpacaConfig: self.core = AlpacaCore(config)
        else: self.core = None
