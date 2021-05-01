from .vectorized_strategy import VectorizedStrategy, filter_dict
from ..data_control import FrameClient
from ..common import indicators, Trade, Portfolio, TradeShortcut
import numpy as np
import pandas as pd

class RenkoMacdStrategy(VectorizedStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        args = filter_dict(locals(), 'self', 'kwargs')
        self.logger.info(f'Configured {self.__class__.__name__} with {args}\n')

        self.close_args = dict(time_in_force='GTC', order_type='AtMarket')
        self.trade_pat = self.portfolio.create_trade_shortcut(
            'rm_pat', is_in_pips=True, time_in_force='GTC',
            order_type='AtMarket', trailing_step=1)

        self.logger.debug(f'Added new trade shortcut in Portfolio({self.portfolio.id}): {self.trade_pat}')

    def _clean_portfolio_positions(self):
        open_pos = self._group_porfolio_positions()
        self.logger.debug(f'Closing {len(open_pos)} opened groups for portfolio({self.portfolio.id})')
        for currency, group in open_pos:
            for idx, row in group[['tradeId', 'amountK']].iterrows():
                self.robot.close_trade(dict(tradeId=id, currency=currency), self.portfolio, amount=row['amountK'], **self.close_args)

    def _prepare_df(self, df):
        renko_df = indicators.RenkoDF(df) # df index is reset in the RenkoDF
        df = df.merge(renko_df.loc[:,["date", "bar_num"]], how="outer", on="date")

        df["bar_num"].fillna(method = 'ffill', inplace = True)
        df.set_index('date', inplace=True)

        client = FrameClient.from_df(df)
        client.macd()
        client.atr()
        client.slope('macd')
        client.slope('macd_signal')

        return client.get_df().dropna()

    def _trade_signal(self, df, last_signal):
        close, signal = False, None
        bar_num = df["bar_num"][-1]
        crossover = (np.sign(df["macd"][-1] - df["macd_signal"][-1]) +
            np.sign(df["macd_slope"][-1] - df["macd_signal_slope"][-1]))

        if last_signal is None:
            if bar_num >= 2 and crossover == 2: signal = "Buy"
            elif bar_num <= -2 and crossover == -2: signal = "Sell"
            
        elif last_signal == "long":
            if bar_num <= -2 and crossover == -2: close, signal = True, "Sell"
            elif crossover == -2: close = True
            
        elif last_signal == "short":
            if bar_num >= 2 and crossover == 2: close, signal = True, "Buy"
            elif crossover == 2: close = True

        if close or signal: self.logger.info(f'Close[{close}], Signal[{signal}] found')
        return close, signal

    def start_run(self):
        self.logger.info(f'Starting the {RenkoMacdStrategy.__name__} strategy')
        super().start_run()

    def end_run(self):
        self.logger.info(f'Finishing the {RenkoMacdStrategy.__name__} strategy')
        self._clean_portfolio_positions()
        super().end_run()

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

                df = self._prepare_df(df)
                self.logger.debug(f'Method update_trades called for {symbol} with {len(df)} items')
                if df.empty: continue

                stop = 8# 1.5 * df['atr'][-1]
                pos_amount = 10#self.portfolio.get_lot_size(symbol)/stop
                close, signal = self._trade_signal(df, last_signal)

                if close:
                    for idx, row in open_pos_cur[['tradeId', 'amountK']].iterrows():
                        robot.close_trade(dict(tradeId=row['tradeId'], currency=symbol),
                            self.portfolio, amount=row['amountK'], **self.close_args)

                if signal == "Buy":
                    trade = trade_pat.create_trade(symbol=symbol, is_buy=True,
                                                   amount=pos_amount, stop=-stop)
                    robot.open_trade(trade, self.portfolio)

                elif signal == "Sell":
                    trade = trade_pat.create_trade(symbol=symbol, is_buy=False,
                                                   amount=pos_amount, stop=-stop)
                    robot.open_trade(trade, self.portfolio)

            except Exception as ex:
                self.logger.warning(f'Error encountered: {ex}')