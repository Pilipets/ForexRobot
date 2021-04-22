import fxcmpy
import pandas as pd
from robot.common import Portfolio
import time

class FxRobot:
    def __init__(self, config):
        self.api = fxcmpy.fxcmpy(
            access_token = config.access_token,
            server= config.server,
            log_level = config.log_level)

    def __del__(self):
        self.api.close()

    def get_last_bar(self, symbol, columns = ['bids'], period = 'm1', n = 1):
        bars : pd.DataFrame = self.api.get_candles(
            symbol, period = period, number = n, columns = columns)

        bars.rename(columns={
            "bidopen": "open", "bidclose": "close", "bidhigh": "high", "bidlow" : "low"},
            inplace=True
        )
        return bars

    def sleep_till_next_bar(self, last_timestamp, timedelta):
        next_timestamp = last_timestamp.tz_localize('utc') + timedelta
        delta = (next_timestamp - pd.Timestamp.utcnow()).total_seconds()

        print('Sleeping for', delta, 'seconds')
        time.sleep(max(0, delta))

    def get_api(self):
        return self.api

    def execute_trades(self, trades):
        if trades: print('Executing', len(trades), 'trades')
