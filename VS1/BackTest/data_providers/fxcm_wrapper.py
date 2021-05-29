import fxcmpy
from .basic_wrapper import DataAPI
from data_filters import fxcm_filter

class FxcmAPI(DataAPI):
    def __init__(self, token):
        self.con = fxcmpy.fxcmpy(access_token = token, log_level = 'error', server='demo')

    def get_candles(self, ticker, *args, **kwargs):
        # con.get_candles(pair, period='m5', number=250)
        # periods can be m1, m5, m15 and m30, H1, H2, H3, H4, H6 and H8, D1, W1, M1

        # defaults
        kwargs['columns'] =  ['askopen', 'askclose', 'askhigh', 'asklow', 'tickqty']

        df = self.con.get_candles(ticker, *args, **kwargs)
        return fxcm_filter(df)

    def __del__(self):
        self.con.close()