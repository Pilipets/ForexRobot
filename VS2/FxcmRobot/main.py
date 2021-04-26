from fxcmpy import fxcmpy
from robot import FxRobot, FxConfig
import pandas as pd

from robot import RenkoMacdStrategy, BbandMacdStrategy
import logging

if __name__ == '__main__':
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
    

    df = strategy.frame_client.df

    api : fxcmpy = bot.api
    api.get_open_positions()
    data = api.get_open_positions()
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
            '%(asctime)s:%(funcName)s:%(lineno)d:%(levelname)s:%(message)s')
    handler.setLevel(logging.ERROR)
    handler.setFormatter(formatter)
    logger = logging.getLogger('temp')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    logger.propagate = False