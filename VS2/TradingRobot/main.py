import logging

def setup_logger(logger_name, fp):
    fmt = '%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s:%(name)s:%(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt)
    fh = logging.FileHandler(fp)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(fmt))

    logger = logging.getLogger(logger_name)
    logger.addHandler(fh)

def test1():
    from robot import TradingRobot, AlpacaConfig
    from robot import ScalpStrategy

    conf = AlpacaConfig.from_file("config/alpaca_config.ini")
    #bot = TradingRobot(conf)

    #portfolio = bot.create_portfolio(['MSFT', 'AAPL'], pile_size = 1000)

    #print(bot.get_core().get_api().get_clock())
    #strategy = ScalpStrategy(portfolio, update_period=30)
    #strategy.run()

if __name__ == '__main__':
    #setup_logger('MainLogger', 'console.log')
    test2()