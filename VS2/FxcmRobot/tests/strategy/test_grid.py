from fxcmpy import fxcmpy
from robot import FxRobot, FxConfig
import pandas as pd

from robot.strategy import GridStrategy

def test_grid():
    config = FxConfig.from_file("config/init_config.ini")
    bot = FxRobot(config)
    portfolio = bot.create_portfolio(['GBP/JPY'], lot_size=15)
    strategy = GridStrategy(
        robot = bot,
        portfolio= portfolio,
        run_for = pd.Timedelta(8, unit='hours'),
        lower_price = 1.156,
        upper_price = 1.5346,
        grid_levels = 5,
        moving_grid=True,
        update_period = pd.Timedelta(60, unit='sec')
    )
    strategy.run()