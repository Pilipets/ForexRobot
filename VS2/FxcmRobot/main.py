from fxcmpy import fxcmpy
from robot import FxRobot, Config
import pandas as pd

from robot import RenkoMacdStrategy

config = Config.from_file("config/fxcm_config.ini")
bot = FxRobot(config)

strategy = RenkoMacdStrategy('EUR/USD', bot, update_period = pd.Timedelta(90, unit='sec'))

strategy.run()
