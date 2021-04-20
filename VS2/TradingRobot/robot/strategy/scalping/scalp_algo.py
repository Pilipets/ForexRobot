import pandas as pd
from enum import Enum

class ScalpAlgo:
    class State(Enum):
        TO_BUY = 0
        BUY_SUBMITTED = 1
        TO_SELL = 2
        SELL_SUBMITTED = 3

    def __init__(self, core, symbol, lot):
        self.core = core
        self.api = core.get_api()
        self.symbol = symbol
        self.lot = lot
        self.bars = pd.DataFrame()


        clock = core.get_clock()
        if not clock.is_open: return
        self.next_close = clock.next_close - pd.Timedelta('7min')

        # ISSUE: The problem is with the free Alpaca API - one can't received last 1 hour date
        # That's why we initialize the bot with no bars
        self._init_state()

    def _init_state(self):
        # One order at a time, state machine which makes transitions
        self.order = None
        self.position = None
        self.state = State.TO_BUY

    def _submit_buy(self):
        last_price = self.api.get_last_trade(self.symbol).price
        amount = int(self.lot / last_price)
        try:
            # TODO: set the stoploss to prevent big loss
            order = self.api.submit_order(
                symbol=self._symbol,
                side='buy',
                type='limit',
                qty=amount,
                time_in_force='day',
                limit_price=trade.price,
            )

        except Exception as ex:
            print('Exception occured when submitting the order:', ex)
            self._transition(State.TO_BUY)
        
        else:
            self.order = order
            print(f'submitted buy {order}')
            self._transition(State.BUY_SUBMITTED)

    def _submit_sell(self, market_closed=False):
        params = dict(
            symbol=self.symbol,
            side='sell',
            qty=self.position.qty,
            time_in_force='day',
        )

        if market_closed:
            params['type'] = 'market'
        else:
            last_price = self.api.get_last_trade(self._symbol).price
            cost_basis = self.position.avg_entry_price
            limit_price = max(cost_basis + 0.01, last_price)

            params.update(dict(
                type='limit',
                limit_price=limit_price,
            ))

        try:
            order = self.core.submit_order(**params)
        except Exception as ex:
            print(ex)
            self._transition(State.TO_SELL)

        else:
            self.order = order
            print(f'submitted sell {order}')
            self._transition(State.SELL_SUBMITTED)

    def _transition(self, new_state):
        print(f'transition from {self._state} to {new_state}')
        self._state = new_state

    def _calc_buy_signal(self):
        mavg = self.bars.rolling(3).mean().close.values
        closes = self.bars.close.values

        if closes[-2] < mavg[-2] and closes[-1] > mavg[-1]:
            print(f'buy signal: closes[-2] {closes[-2]} < mavg[-2] {mavg[-2]}',
                  f'closes[-1] {closes[-1]} > mavg[-1] {mavg[-1]}')
            return True
        else:
            print(f'closes[-2:] = {closes[-2:]}, mavg[-2:] = {mavg[-2:]}')
            return False

    def _outofmarket(self):
        return self.core.now() >= self.next_close

    def _cancel_order(self):
        order = self.order
        print(f'canceling missed buy order {order.id} at {order.limit_price} after 2 min')

    def on_bar(self, bar):
        self._bars = self._bars.append(pd.DataFrame({
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume}, index=[bar.timestamp])
        )

        print(f'received bar start = {bar.timestamp}, close = {bar.close}, len(bars) = {len(self._bars)}')
        if len(self.bars) < 4:
            return
        if self._outofmarket():
            return
        if self.state == State.TO_BUY:
            if self._calc_buy_signal():
                self._submit_buy()

    def on_order_update(self, event, order):
        print(f'order update: {event} = {order}')
        if event == 'fill':
            self.order = None
            if self.state == State.BUY_SUBMITTED:
                self.position = self.api.get_position(self._symbol)
                self._transition(State.TO_SELL)
                self._submit_sell()
            elif self._state == State.SELL_SUBMITTED:
                self.position = None
                self._transition(State.TO_BUY)

        elif event == 'partial_fill':
            self.position = self.api.get_position(self._symbol)
            self.order = self.api.get_order(order['id'])

        elif event in ('canceled', 'rejected'):
            if event == 'rejected':
                print(f'order rejected: current order = {self._order}')
            self.order = None
            if self.state == State.BUY_SUBMITTED:
                if self.position is not None:
                    self._transition(State.TO_SELL)
                    self._submit_sell()
                else:
                    self._transition(State.TO_BUY)
            elif self.state == State.SELL_SUBMITTED:
                self._transition(State.TO_SELL)
                self._submit_sell(bailout=True)
            else:
                print(f'unexpected state for {event}: {self._state}')

    def on_position(self, position):
        # We have active position on self.symbol
        print('on_position for', position.symbol)

        now = self.core.now()
        order = self.order
        if self.state == State.BUY_SUBMITTED and now - self.order.submitted_at > pd.Timedelta('3min'):
            self._cancel_order()

        if self.position is not None and self._outofmarket():
            self._submit_sell(market_closed=True)


