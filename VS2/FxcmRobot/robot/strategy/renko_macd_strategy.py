from .base_strategy import BaseStrategy
from ..data_control import FrameClient
from ..common import indicators
import numpy as np

class RenkoMacdStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

    def trade_signal(self, df, l_s):
        signal = ""

        bar_num = df["bar_num"][-1]
        crossover = np.sign(df["macd"][-1] - df["macd_signal"][-1]) + np.sign(df["macd_slope"][-1] - df["macd_signal_slope"][-1])

        if l_s == "":
            if bar_num >= 2 and crossover == 2: signal = "Buy"
            elif bar_num <= -2 and crossover == -2: signal = "Sell"
            
        elif l_s == "long":
            if bar_num <= -2 and crossover == -2: signal = "Close_Sell"
            elif crossover == -2: signal = "Close"
            
        elif l_s == "short":
            if bar_num >= 2 and crossover == 2: signal = "Close_Buy"
            elif crossover == 2: signal = "Close"

        return signal

    def get_trades(self, df):
        print('Check get_trades called with', len(df), 'items')
        api = self.robot
        symbol = self.symbol

        try:
            open_pos = api.get_open_positions()
            if len(open_pos) == 0: return

            long_short = ""
            open_pos_cur = open_pos.loc[open_pos["currency"] == symbol, "isBuy"]
            if not open_pos_cur.empty:
                if open_pos_cur.iloc[0] == True: long_short = "long"
                else: long_short = "short"
            
            df = self.prepare_df(df)
            signal = self.trade_signal(df, long_short)
            
            if signal == "Buy":
                api.open_trade(symbol=symbol, is_buy=True, is_in_pips=True, amount=3, time_in_force='GTC', order_type='AtMarket')
                print("New long position initiated for ", symbol)

            elif signal == "Sell":
                api.open_trade(symbol=symbol, is_buy=False, is_in_pips=True, amount=3, time_in_force='GTC', order_type='AtMarket')
                print("New short position initiated for ", symbol)

            elif signal == "Close":
                api.close_all_for_symbol(symbol)
                print("All positions closed for ", symbol)
                
            elif signal == "Close_Buy":
                api.close_all_for_symbol(symbol)
                print("Existing Short position closed for ", symbol)
                api.open_trade(symbol=symbol, is_buy=True, is_in_pips=True, amount=3, time_in_force='GTC', order_type='AtMarket')
                print("New long position initiated for ", symbol)

            elif signal == "Close_Sell":
                api.close_all_for_symbol(symbol)
                print("Existing long position closed for ", symbol)
                api.open_trade(symbol=symbol, is_buy=False, is_in_pips=True, amount=3, time_in_force='GTC', order_type='AtMarket')
                print("New short position initiated for ", symbol)

        except Exception as ex:
            print(ex)
            print("error encountered....skipping this iteration")