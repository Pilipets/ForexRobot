import time
import pandas as pd

from .. import FxRobot
from ..data_control import FrameClient
from .base_strategy import BaseStrategy, filter_dict

class VectorizedStrategy(BaseStrategy):
    def __init__(self, update_period, bars_period, update_bars_cnt = 1,
                trigger_frame_size = 0, max_frame_size = 500, init_bars_cnt = 0,
                **kwargs):
        super().__init__(**kwargs)

        args = filter_dict(locals(), 'self', 'kwargs')
        self.logger.info(f'Configured {self.__class__.__name__} with {args}\n')

        self.frame_clients = [FrameClient(max_frame_size) for _ in range(len(self.symbols))]

        self.update_period = update_period
        self.bars_period = bars_period
        self.update_bars_cnt = update_bars_cnt
        self.trigger_frame_size = trigger_frame_size
        self.init_bars_cnt = init_bars_cnt

    def _group_porfolio_positions(self):
        data = self.robot.get_open_positions()
        if data.empty: return data.groupby([])

        grouped = data.loc[(data['currency'].isin(self.portfolio.get_symbols()))
                           & (data['orderId'].isin(self.portfolio.get_order_ids())),
                           ['currency','isBuy', 'tradeId', 'orderId','amountK']]
        return grouped.groupby(['currency'])

    def start_run(self):
        if not self.init_bars_cnt: return

        for idx, symbol in enumerate(self.symbols):
            try:
                self.logger.debug(f'Initializing {symbol} frame with {self.init_bars_cnt} elements')
                data = self.robot.get_last_bar(symbol, period = self.bars_period, n = self.init_bars_cnt)
                self.frame_clients[idx].add_rows(data)
            except Exception as ex:
                self.logger.warning(f'Exception received: {ex}\n')

    def update_trades(self):
        pass

    def iter_run(self):
        robot : FxRobot = self.robot

        df_updates = [(pd.DataFrame(), False) for _ in range(len(self.symbols))]
        last_bar_time = None
        for idx, symbol in enumerate(self.symbols):
            try:
                self.logger.info(f'Processing {symbol} update')
                data = robot.get_last_bar(symbol, period = self.bars_period, n = self.update_bars_cnt)
                if data.empty: continue

                print(data.index[-1])
                if last_bar_time is None: last_bar_time = data.index[-1]
                else: last_bar_time = min(last_bar_time, data.index[-1])

                client = self.frame_clients[idx]
                if client.add_rows(data):
                    self.logger.debug(f'Data update happened for {symbol}')
                    
                    client.update()
                    if self.trigger_frame_size <= client.get_size():
                        trigger_df = client.get_last_bars(self.trigger_frame_size)
                        df_updates[idx] = trigger_df, True

            except Exception as ex:
                self.logger.warning(f'Exception received: {ex}\n')

        self.update_trades(df_updates)

        if last_bar_time is None:
            last_bar_time = pd.Timestamp.utcnow() - self.update_period

        robot.sleep_till_next_bar(last_bar_time, self.update_period)
        self.logger.info('\n')