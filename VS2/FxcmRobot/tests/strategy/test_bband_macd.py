from fxcmpy import fxcmpy
from robot import FxRobot, FxConfig
import pandas as pd

from robot.strategy import BBandMacdStrategy

def test_bband_macd():
    config = FxConfig.from_file("config/init_config.ini")
    bot = FxRobot(config)
    portfolio = bot.create_portfolio(['EUR/USD', 'GBP/JPY'], {'EUR/USD': 10}, 15)
    
    strategy = BBandMacdStrategy(
        robot = bot,
        portfolio = portfolio,
        bars_period = 'm1',
        update_period = pd.Timedelta(95, unit='sec'),
        init_bars_cnt = 100,
        trigger_frame_size = 100,
        run_for = pd.Timedelta(15, unit='min')
    )
    
    strategy.run()
