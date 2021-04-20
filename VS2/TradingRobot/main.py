from robot import TradingRobot, AlpacaConfig

conf = AlpacaConfig.from_file("config/alpaca_config.ini")
bot = TradingRobot(conf)

print(bot.get_clock())

portfolio = bot.create_portfolio(['MSFT', 'AAPL'])


from robot import ScalpStrategy
strategy = ScalpStrategy(portfolio)

strategy.run()
