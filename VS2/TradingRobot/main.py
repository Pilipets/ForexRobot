from robot import TradingRobot, AlpacaConfig

import logging

def setup_logger(logger_name, fp):
    fmt = '%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s:%(name)s:%(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt)
    fh = logging.FileHandler(fp)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(fmt))

    logger = logging.getLogger(logger_name)
    logger.addHandler(fh)

from robot import ScalpStrategy
if __name__ == '__main__':
    setup_logger('MainLogger', 'console.log')

    conf = AlpacaConfig.from_file("config/alpaca_config.ini")
    bot = TradingRobot(conf)

    portfolio = bot.create_portfolio(['MSFT', 'AAPL'], 1000, 0.03)
    print(bot.get_core().get_api().get_clock())
    strategy = ScalpStrategy(portfolio, update_period=30)
    strategy.run()