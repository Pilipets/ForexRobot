from .basic_wrapper import DataAPI
from alpha_vantage.timeseries import TimeSeries

from data_filters import alpha_vintage_filter

class AlphaVintageAPI(DataAPI):
    def __init__(self, token):
        self.ts = TimeSeries(key=token, output_format='pandas')

    def get_candles(self, ticker,  **kwargs):
        data = self.ts.get_intraday(symbol=ticker, outputsize='full', **kwargs)[0]
        return alpha_vintage_filter(data)

    def __getattr__(self, attr):
        return getattr(self.ts, attr)
