def log_method(*args):
    print(args)
    print('args finished')


from fxcmpy import fxcmpy
from robot import FxRobot, FxConfig

config = FxConfig.from_file("config/init_config.ini")
bot = FxRobot(config)
api.subscribe_data_model('Order', [log_method])

