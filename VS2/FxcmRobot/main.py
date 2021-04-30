from fxcmpy import fxcmpy
from robot import FxRobot, FxConfig
import pandas as pd

from robot.strategy import RenkoMacdStrategy

def log_method(*args):
    print(args)
    print('args finished')

def renko_macd_test():
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

    api : fxcmpy = bot.api
    data = api.get_open_positions()
    
    api.subscribe_data_model('Order', [log_method])

from fxcmpy import fxcmpy
from robot import FxRobot, FxConfig
import pandas as pd
from robot.strategy import GridStrategy

config = FxConfig.from_file("config/init_config.ini")
bot = FxRobot(config)
strategy = GridStrategy(
    robot = bot,
    symbol= 'EUR/USD',
    lower_price = 1.156,
    upper_price = 1.5346,
    grid_levels = 5,
    grid_type = GridStrategy.SYMMETRIC_TYPE
)

strategy._init_grid()
trade_price = bot.get_offers(['EUR/USD'], ['sell', 'buy'])
data = api.get_offers()
data2 = data[data['currency'].isin(['EUR/USD'])]
