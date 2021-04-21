from robot import FxRobot, Config
from fxcmpy import fxcmpy

config = Config.from_file("config/fxcm_config.ini")
bot = FxRobot(config)

api : fxcmpy = bot.get_api()

#data = api.get_candles('EUR/USD', period='m1', number=50)

print(data)

api.fxcmpy