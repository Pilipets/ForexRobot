from adv_backtesting import BBandSimulator
import os.path
from data_providers import ProviderType, get_data_provider
import data_filters
import pandas as pd

majors_data_dir = 'E:\Programming\Trading\Data\Forex'
majors_csv = {'EUR/USD' : 'EURUSD_Candlestick_1_D_ASK_01.03.2014-13.03.2021.csv'}

api = get_data_provider(ProviderType.CSV)

ticker = 'EUR/USD'
fp = os.path.join(majors_data_dir, majors_csv[ticker])

data = api.get_candles(ticker, fp, parse_dates = ["Local time"])
data = data_filters.dukascopy_filter(data)

strategy = BBandSimulator(ticker, data, atr_period = 20,
                          bb_period = 20, std = 2, sma_fast = 50, sma_slow = 200)
strategy.test_strategy(open_limit = 4, balance = 10000)

strategy.get_stats(1)
strategy.plot('Boolinger Bands + MA')
