import pandas as pd
from .basic_wrapper import DataAPI

class CsvAPI(DataAPI):
    def get_candles(self, ticker, *args, **kwargs):
        if not 'date_parser' in kwargs: kwargs['date_parser'] = lambda col: pd.to_datetime(col, utc=True)
        return pd.read_csv(*args, **kwargs)
