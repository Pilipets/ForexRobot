import time
import pandas as pd

from .. import FxRobot
from ..data_control import FrameClient
from .base_strategy import BaseStrategy, filter_dict

class VectorizedStrategy(BaseStrategy):
    def __init__(self, update_period, bars_period, update_bars_cnt = 1,
                trigger_frame_size = 0, max_frame_size = 500,
                init_bars_cnt = 0, **kwargs):
        super().__init__(**kwargs)

        args = filter_dict(locals(), 'self', 'kwargs')
        self.logger.info(f'Configured {self.__class__.__name__} with {args}\n')

        self.frame_clients = [FrameClient(max_frame_size) for _ in range(len(self.symbols))]

        self.update_period = update_period
        self.bars_period = bars_period
        self.update_bars_cnt = update_bars_cnt
        self.trigger_frame_size = trigger_frame_size
        self.init_bars_cnt = init_bars_cnt

    def start_run(self):
        self.logger.info(f'Starting the {self.__class__.__name__} strategy')
        super().start_run()
        if not self.init_bars_cnt: return

        for idx, symbol in enumerate(self.symbols):
            try:
                self.logger.debug(f'Initializing {symbol} frame with {self.init_bars_cnt} elements')
                data = self.robot.get_last_bar(symbol, period = self.bars_period, n = self.init_bars_cnt)
                self.frame_clients[idx].add_rows(data)
            except Exception as ex:
                self.logger.warning(f'Exception received: {ex}\n')

    def end_run(self):
        self.logger.info(f'Finishing the {self.__class__.__name__} strategy')
        super().end_run()

    def iter_run(self):
        robot : FxRobot = self.robot

        df_updates = [(pd.DataFrame(), False) for _ in range(len(self.symbols))]
        last_bar_time = None
        for idx, symbol in enumerate(self.symbols):
            try:
                self.logger.info(f'Processing {symbol} update')
                data = robot.get_last_bar(symbol, period = self.bars_period, n = self.update_bars_cnt)
                if data.empty: continue

                if last_bar_time is None: last_bar_time = data.index[-1]
                else: last_bar_time = max(last_bar_time, data.index[-1])

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
            last_bar_time = pd.Timestamp.utcnow()

        robot.sleep_till_next_bar(last_bar_time, self.update_period)
        self.logger.info('\n')

    def trade_signal(self, symbol, df, last_signal):
        return False, None

    def prepare_df(self, df):
        return df

    def update_trades(self, df_updates):
        robot = self.robot
        trade_pat : TradeShortcut = self.trade_pat

        if not any(updated for _, updated in df_updates): return

        open_pos = self._group_porfolio_positions()
        for idx, (df, updated) in enumerate(df_updates):
            try:
                if not updated: continue
                symbol = self.symbols[idx]
                
                open_pos_cur = pd.DataFrame()
                last_signal = None
                if symbol in open_pos.groups:
                    open_pos_cur = open_pos.get_group(symbol)
                    
                    if open_pos_cur['isBuy'].iloc[0] == True: last_signal = 'long'
                    else: last_signal = 'short'

                df = self.prepare_df(df)
                self.logger.debug(f'Method update_trades called for {symbol} with {len(df)} items')
                if df.empty: continue

                close, trade = self.trade_signal(symbol, df, last_signal)

                if close:
                    for id in open_pos_cur['tradeId']:
                        robot.close_trade(dict(tradeId=int(row[id]), currency=symbol),
                                          self.portfolio, **close)

                if trade:
                    robot.open_trade(trade, self.portfolio)

            except Exception as ex:
                self.logger.warning(f'Error encountered: {ex}')