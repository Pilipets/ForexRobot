import os.path
from data_providers import ProviderType, get_data_provider
import data_filters
from adv_backtesting import RenkoMACDSimulator
import pandas as pd

majors_data_dir = 'E:\Programming\Trading\Data\Forex'
majors_csv = {'USD/JPY' : 'USDJPY_Candlestick_1_D_ASK_01.03.2014-13.03.2021.csv'}

api = get_data_provider(ProviderType.CSV)

ticker = 'USD/JPY'
fp = os.path.join(majors_data_dir, majors_csv[ticker])

data = api.get_candles(ticker, fp, parse_dates = ["Local time"])
data = data_filters.dukascopy_filter(data)
strategy = RenkoMACDSimulator(ticker, data,
                              renko_brick_size = 0.5, atr_period = 120,
                              macd_a = 12, macd_b = 26, macd_c = 9,
                              slope_period = 5)


df = strategy.df

strategy.test_strategy(3, 10000)
strategy.get_stats(1)
strategy.plot('Renko_MACD')
df = strategy.res_df
balance = strategy.balance