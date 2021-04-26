from .base_strategy import BaseStrategy
from ..data_control import FrameClient
from ..common import indicators, Trade, Portfolio, TradeShortcut
import numpy as np

class RenkoMacdStrategy(BaseStrategy):
    def __init__(self, robot, portfolio : Portfolio, **kwargs):
        super().__init__(robot = robot, portfolio = portfolio, **kwargs)
        self.logger.info(f'Configured {RenkoMacdStrategy.__name__} with porfolio({portfolio.id})')

        self.close_args = dict(time_in_force='GTC', order_type='AtMarket')
        self.trade_pat = self.portfolio.create_trade_shortcut(
            'rm_pat', is_in_pips=True, time_in_force='GTC', order_type='AtMarket')

    def _clean_positions(self):
        for symbol in self.symbols:
            self.robot.close_all_positions_for(symbol, **self.close_args)

    def run(self):
        self.logger.info(f'Starting the {RenkoMacdStrategy.__name__} strategy')
        self._clean_positions()
        super().run()
        self.logger.info(f'Finishing the {RenkoMacdStrategy.__name__} strategy')
        self._clean_positions()

    def prepare_df(self, df):
        renko_df = indicators.RenkoDF(df) # df index is reset in the RenkoDF
        df = df.merge(renko_df.loc[:,["date", "bar_num"]], how="outer", on="date")

        df["bar_num"].fillna(method = 'ffill', inplace = True)
        df.set_index('date', inplace=True)

        client = FrameClient.from_df(df)
        client.macd()
        client.slope('macd')
        client.slope('macd_signal')

        return client.get_df().dropna()

    def trade_signal(self, df, last_signal):
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

        if close or signal: self.logger.info(f'Close[{close}], Signal[{signal} found')
        return close, signal

    def update_trades(self, df_updates):
        robot = self.robot
        trade_pat : TradeShortcut = self.trade_pat

        open_pos = robot.get_open_positions()
        for idx, (df, updated) in enumerate(df_updates):
            try:
                if not updated: continue
                symbol = self.symbols[idx]
                lot = self.portfolio.get_lot_size(symbol)

                last_signal = None
                if len(open_pos) > 0:
                    open_pos_cur = open_pos.loc[open_pos["currency"] == symbol, "isBuy"]

                    if len(open_pos_cur) > 0:
                        if open_pos_cur.iloc[0] == True: last_signal = "long"
                        else: last_signal = "short"
            
                df = self.prepare_df(df)
                self.logger.debug(f'Method update_trades called for {symbol} with {len(df)} items')
                close, signal = self.trade_signal(df, last_signal)
            
                if close:
                    robot.close_all_positions_for(symbol, self.portfolio, **self.close_args)

                if signal == "Buy":
                    trade = trade_pat.create_trade(symbol=symbol, is_buy=True, amount=lot)
                    robot.execute_trade(trade, self.portfolio)

                elif signal == "Sell":
                    trade = trade_pat.create_trade(symbol=symbol, is_buy=False, amount=lot)
                    robot.execute_trade(trade, self.portfolio)

            except Exception as ex:
                self.logger.warning(f'Error encountered: {ex}')