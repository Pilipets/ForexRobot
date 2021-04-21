import fxcmpy
from robot.common import Portfolio

class FxRobot:
    def __init__(self, config):
        self.api = fxcmpy.fxcmpy(
            access_token = config.access_token,
            server= config.server,
            log_level = config.log_level)

        self.strategies = {}

    def __del__(self):
        self.api.close()

    def get_api(self):
        return self.api