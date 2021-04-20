from robot import TradingRobot, AlpacaConfig

conf = AlpacaConfig.from_file("config/alpaca_config.ini")
bot = TradingRobot(conf)


portfolio = bot.create_portfolio(['MSFT', 'AAPL'])


from robot import ScalpStrategy
strategy = ScalpStrategy(portfolio)

