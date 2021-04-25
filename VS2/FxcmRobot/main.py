from fxcmpy import fxcmpy
from robot import FxRobot, Config
import pandas as pd

from robot import RenkoMacdStrategy, BbandMacdStrategy

config = Config.from_file("config/fxcm_config.ini")
bot = FxRobot(config)

bot = None
portfolio = bot.create_portfolio(['EUR/USD'], 1500)

strategy = RenkoMacdStrategy(
    portfolio = portfolio,
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

portfolio = bot.create_portfolio(['EUR/USD'], 1500)
s1 = portfolio.create_trade_shortcut(
    'renko_macd_1',
    is_buy=True, is_in_pips=True,
    time_in_force='GTC',
    order_type='AtMarket'
)

trade = s1.create_trade(symbol='EUR/USD', amount = 5)
print(trade)

data = bot.get_last_bar('EUR/USD')