import os.path
from data_providers import ProviderType, get_data_provider
import data_filters
import pandas as pd

majors =  ['AUD/USD', 'EUR/USD', 'GBP/USD', 'NZD/USD', 'USD/CAD', 'USD/CHF', 'USD/JPY']
majors_data_dir = 'E:/Programming/Trading/Data/Forex'
majors_csv = {'AUD/USD' : 'AUDUSD_Candlestick_1_D_ASK_01.03.2014-13.03.2021.csv',
              'EUR/USD' : 'EURUSD_Candlestick_1_D_ASK_01.03.2014-13.03.2021.csv',
              'GBP/USD' : 'GBPUSD_Candlestick_1_D_ASK_01.03.2014-13.03.2021.csv',
              'NZD/USD' : 'NZDUSD_Candlestick_1_D_ASK_01.03.2014-13.03.2021.csv',
              'USD/CAD' : 'USDCAD_Candlestick_1_D_ASK_01.03.2014-13.03.2021.csv',
              'USD/CHF' : 'USDCHF_Candlestick_1_D_ASK_01.03.2014-13.03.2021.csv',
              'USD/JPY' : 'USDJPY_Candlestick_1_D_ASK_01.03.2014-13.03.2021.csv' }

def test1():
    api = get_data_provider(ProviderType.CSV)

    strategies = []
    data = {}
    for ticker in majors:
        fp = os.path.join(majors_data_dir, majors_csv[ticker])

        df = api.get_candles(ticker, fp, parse_dates = ["Local time"])
        df = data_filters.dukascopy_filter(df)

        strategy = SMABacktester(ticker, df, 50, 200)
        data[ticker] = strategy.test_strategy()
        strategies.append(strategy)
    
    summary = pd.DataFrame(data).T
    summary.columns = ['perf', 'mean', 'std']
    print(summary)

    import matplotlib.pyplot as plt
    summary.plot(kind = "scatter", x = "std", y = "mean", figsize = (15,12), fontsize = 15, s = 50)
    for i in summary.index:
        plt.annotate(i, xy=(summary.loc[i, "std"]+0.0002, summary.loc[i, "mean"]+0.0002), size = 15)
    plt.xlabel("ann. Risk(std)", fontsize = 15)
    plt.ylabel("ann. Return", fontsize = 15)
    plt.title("Risk/Return", fontsize = 20)
    plt.show()

    for i, ticker in enumerate(majors):
        strategy = strategies[i]
        params, stats = strategy.optimize_parameters((25, 50, 1), (75, 200, 1))

        print(ticker, params)
        summary.loc[ticker] = stats

    print(summary)

    summary.plot(kind = "scatter", x = "std", y = "mean", figsize = (15,12), fontsize = 15, s = 50)
    for i in summary.index:
        plt.annotate(i, xy=(summary.loc[i, "std"]+0.0002, summary.loc[i, "mean"]+0.0002), size = 15)
    plt.xlabel("ann. Risk(std)", fontsize = 15)
    plt.ylabel("ann. Return", fontsize = 15)
    plt.title("Risk/Return", fontsize = 20)
    plt.show()
    
#test1()

api = get_data_provider(ProviderType.ALPHA_VINTAGE)
date = api.get_candles('MSFT', interval='5min')
print(type(date.index[0]))
