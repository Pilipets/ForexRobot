from robot import AlpacaBot, AlpacaConfig

conf = AlpacaConfig.from_file("config/alpaca_config.ini")
bot = AlpacaBot(conf)


portfolio = bot.create_portfolio()

