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
    run_for = pd.Timedelta(1, unit='min')
)

strategy.run()

df = strategy.frame_client.df

api : fxcmpy = bot.api

data = api.get_open_positions_summary()


from robot.common import indicators

df2 = df.copy()
df3 = indicators.RenkoDF(df2)
df4 = df2.merge(df3.loc[:,["date", "bar_num"]], how="outer", on="date")
df4["bar_num"].fillna(method = 'ffill', inplace = True)
df4.set_index('date', inplace=True)

df4 = strategy.temp