from datetime import timedelta

from tech_indicators import ATR, BollingerBands
from backtesting import Trade, StatsBackTestSimulator

# Combination of Bollinger bands with mean cross
class BBandSimulator(StatsBackTestSimulator):
    def __init__(self, ticker, df, **params):
        super().__init__(ticker, df, **params)
        
    def _process_df(self, sma_fast, sma_slow, atr_period, bb_period, std):
        data = self.df

        data['SMA_slow'] = data['Close'].rolling(sma_slow).mean()
        data['SMA_fast'] = data['Close'].rolling(sma_fast).mean()
        data['ATR'] = ATR(data, atr_period)
        data = BollingerBands(data, bb_period, std)
        data.dropna(inplace=True)

        self.df = data

    def test_strategy(self, open_limit, balance, ATR_SL = 0.5, risk_rate = 0.05):
        # Initialize testing
        super()._reset_trades(balance, risk_rate)

        df = self.df
        for i in range(1, len(self.df) - 1):
            cur_price = df['Close'][i]

            # Enter trades---------------------------------------------------------------------------
            # 1. Buy
            if len(self.open_trades) < open_limit and df['SMA_fast'][i-1] > df['SMA_slow'][i-1] \
                and 0.5 >= df['BB_percent'][i] >= 0.2:

                take_profit, stop_loss = df['ATR'][i] * 2 * ATR_SL, -df['ATR'][i] * ATR_SL
                self.set_new_trade(i, type = Trade.Type.LONG, entry_price = cur_price,
                                   take_profit = take_profit, stop_loss = stop_loss)
            
            # 2. Sell
            if len(self.open_trades) < open_limit and df['SMA_fast'][i-1] < df['SMA_slow'][i-1] \
                and 0.5 <= df['BB_percent'][i] <= 0.8:

                take_profit, stop_loss = -df['ATR'][i] * 2 * ATR_SL, df['ATR'][i] * ATR_SL
                self.set_new_trade(i, type = Trade.Type.SHORT, entry_price = cur_price,
                                   take_profit = take_profit, stop_loss = stop_loss)

            # Exit profit or stop loss trades---------------------------------------------------------------
            self.safe_exit_trades(i)

            # Long exit after 12 hours-----------------------------------------------------------------
            cur_date = df.index[i]
            self.force_exit_trades(i, lambda x: (x.date - cur_date)/timedelta(hours=1) >= 12)

        # Force exit on all trades---------------------------------------------------------------------
        if len(self.df):
            self.force_exit_trades(i+1, lambda x: True)