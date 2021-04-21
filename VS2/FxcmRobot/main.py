from fxcmpy import fxcmpy
from robot import FxRobot, Config

from robot import RenkoMacdStrategy

config = Config.from_file("config/fxcm_config.ini")
bot = FxRobot(config)

import pandas as pd
df = pd.DataFrame()
data = bot.get_last_bar('EUR/USD', period = 'm1', n = 1)

df = df.append(data)
data = bot.get_last_bar('EUR/USD', period = 'm1', n = 1)

print(df.tail().index == data.index)
