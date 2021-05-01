from fxcmpy import fxcmpy
from robot import FxRobot, FxConfig
import pandas as pd

from robot.strategy import RenkoMacdStrategy

def test_renko_macd():
    config = FxConfig.from_file("config/init_config.ini")

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

test_renko_macd()
