from .trade import Trade

class BackTestSimulator:
    def __init__(self, ticker, df, **params):
        self.ticker = ticker
        self.df = df.copy()

        self._process_df(**params)
        self._reset_trades(0, 0)

    def _process_df(self, **params):
        pass

    def _reset_trades(self, balance, risk_rate):
        self.initial_balance = balance
        self.risk_rate = risk_rate

        self.balance = balance
        self.closed_trades = []
        self.open_trades = set()

    def set_new_trade(self, bar_idx, **kwargs):
        kwargs['date'] = self.df.index[bar_idx]
        kwargs['take_profit'] += kwargs['entry_price']
        kwargs['units'] = int(self.initial_balance * self.risk_rate / max(abs(kwargs['stop_loss']), 1e-5))
        kwargs['stop_loss'] += kwargs['entry_price']
        
        trade = Trade(**kwargs)
        self.open_trades.add(trade)

        # ------------------------------- LOGGING ------------------------------
        msg = 'New Long trade at price:' if trade.is_long() else 'New Short trade at price:'
        print(trade.id,
              msg, round(trade.entry_price, 4),
              'On day:', trade.date,
              'Ticker:', self.ticker, '\n')

    def safe_exit_trades(self, bar_idx):
        cur_price = self.df['Close'][bar_idx]

        for trade in self.open_trades.copy():
            trade.update(cur_price)
            if not trade.closed: continue

            self.balance += trade.result
            self.closed_trades.append(trade)
            self.open_trades.remove(trade)

            # ------------------------------- LOGGING --------------------------------------
            if trade.is_long():
                msg = 'Long profit at price:' if trade.result > 0 else 'Long loss at price:'
            else:
                msg = 'Short profit at price:' if trade.result > 0 else 'Short loss at price:'

            print(trade.id,
                  msg, round(cur_price, 4),
                  'On day:', self.df.index[bar_idx],
                  'With value:', round(trade.result, 4),
                  'Ticker:', self.ticker, '\n')

    def force_exit_trades(self, bar_idx, pred):
        cur_price = self.df['Close'][bar_idx]
        for trade in self.open_trades.copy():
            if not pred(trade): continue

            trade.close(cur_price)

            self.balance += trade.result
            self.closed_trades.append(trade)
            self.open_trades.remove(trade)

            # ------------------------------- LOGGING --------------------------------------
            if trade.is_long():
                msg = 'Force long profit at price:' if trade.result > 0 else 'Force long loss at price:'
            else:
                msg = 'Force short profit at price:' if trade.result > 0 else 'Force short loss at price:'

            print(trade.id,
                  msg, round(cur_price, 4),
                  'On day:', self.df.index[bar_idx],
                  'With value:', round(trade.result, 4),
                  'Ticker:', self.ticker, '\n')
