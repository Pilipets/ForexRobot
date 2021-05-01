def log_method(*args):
    print(args)
    print('args finished')


from fxcmpy import fxcmpy
from robot import FxRobot, FxConfig
import pandas as pd
from robot.strategy import GridStrategy


config = FxConfig.from_file("config/init_config.ini")
bot = FxRobot(config)
portfolio = bot.create_portfolio(['EUR/USD', 'GBP/CAD'], 1500)
api.subscribe_data_model('Order', [log_method])



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
