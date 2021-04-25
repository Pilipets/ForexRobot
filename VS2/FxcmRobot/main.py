from fxcmpy import fxcmpy
from robot import FxRobot, Config
import pandas as pd

from robot import RenkoMacdStrategy, BbandMacdStrategy

config = Config.from_file("config/fxcm_config.ini")
bot = FxRobot(config)

portfolio = bot.create_portfolio(['EUR/USD', 'GBP/CAD'], 1500)

strategy = RenkoMacdStrategy(
    robot = bot,
    portfolio = portfolio,
    bars_period = 'm1',
    update_period = pd.Timedelta(95, unit='sec'),
    init_bars_cnt = 300,
    trigger_frame_size = 300,
    run_for = pd.Timedelta(15, unit='min')
)

strategy.run()

df = strategy.frame_client.df

api : fxcmpy = bot.api

data = api.get_open_positions()