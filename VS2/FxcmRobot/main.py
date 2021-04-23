from fxcmpy import fxcmpy
from robot import FxRobot, Config
import pandas as pd

from robot import RenkoMacdStrategy, BbandMacdStrategy

config = Config.from_file("config/fxcm_config.ini")
bot = FxRobot(config)

strategy = RenkoMacdStrategy(
    symbol = 'EUR/USD',
    robot = bot,
    bars_period = 'm1',
    update_period = pd.Timedelta(95, unit='sec'),
    init_bars_cnt = 300,
    trigger_frame_size = 250,
    run_for = pd.Timedelta(15, unit='min')
)

strategy.run()

df = strategy.frame_client.df

api : fxcmpy = bot.api

data = api.get_open_positions()
d1 = api.get_open_position(70330609)

data = bot.get_last_bar('EUR/USD', period = 'm1', n = 300)

open_pos = api.get_open_positions()

temp = open_pos.loc[open_pos['currency'] == 'BTC/USD', "isBuy"]
temp.iloc[-1]
