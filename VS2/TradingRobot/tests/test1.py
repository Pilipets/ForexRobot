from alpaca_trade_api.rest import REST, TimeFrame
api = REST()
api.get_account()

res = api.get_bars(symbol= 'MSFT', timeframe=TimeFrame.Minute, start="2021-02-08", end="2021-04-18", limit=200).df
res.index = res.index.tz_convert('Europe/Kiev')

res_set = api.get_barset('MSFT', timeframe='15Min', limit=200)
d1 = res_set.get('MSFT').df

api.get_last_trade()