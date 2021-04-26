import fxcmpy
import pandas as pd
from .common import Portfolio, Trade
import time
import logging
from .fx_config import FxConfig

class FxRobot:
    def __init__(self, config : FxConfig):
        self._setup_logger(logging.getLevelName(config.log_level))

        self.logger.info(f'Configured {FxRobot.__name__} with {config}')
        self.api = fxcmpy.fxcmpy(
            access_token = config.fxcm_config.access_token,
            server= config.fxcm_config.server,
            log_level = config.fxcm_config.log_level)

    def _setup_logger(self, log_level):
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s:%(funcName)s:%(lineno)d:%(levelname)s:%(name)s:%(message)s')
        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(FxRobot.__name__)
        self.logger.setLevel(log_level)
        self.logger.addHandler(handler)
        self.logger.propagate = False

    def __del__(self):
        self.api.close()

    def get_last_bar(self, symbol, columns = ['bids'], period = 'm1', n = 1):
        self.logger.debug(f'Querying last {n} bars for {symbol}')
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

        self.logger.debug(f'Sleeping till next data update for {delta} seconds')
        time.sleep(max(0, delta))

    def get_api(self):
        return self.api

    def get_logger(self):
        return self.logger

    def create_portfolio(self, symbols, pile_size, **kwargs):
        portfolio = Portfolio(symbols, pile_size, **kwargs)
        self.logger.info(f'Created new portfolio object with id({portfolio.id}): {portfolio}')
        return portfolio

    def __getattr__(self, name):
        return getattr(self.api, name)

    def execute_trade(self, trade : Trade, portfolio : Portfolio):
        self.logger.info(f'Executing new trade for portfolio({portfolio.id}): {trade}')
        return self.api.open_trade(**trade.get_fxcm_args())

    def close_all_positions_for(self, symbol, **args):
        self.logger.info(f'Closing all positions for {symbol} with args {args}')
        self.api.close_all_for_symbol(symbol, **args)