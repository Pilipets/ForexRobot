
class DataAPI:
    def _unify_data(self):
        raise NotImplementedError()

    def get_candles(self, ticker, *args, **kwargs):
        raise NotImplementedError()