from ..common import Portfolio
from ..alpaca_internals import AlpacaCore

from alpaca_trade_api.rest import TimeFrame

import asyncio
import time
import pandas as pd

class ScalpAlgo:
    def __init__(self, core : AlpacaCore, symbol, lot = 10):
        self._core = core
        self._symbol = symbol
        self._lot = lot
        self._bars = pd.DataFrame()

        clock = core.get_clock()
        if not clock.is_open: return
        self._next_close = clock.next_close - pd.Timedelta('5min')

        # ISSUE: The problem is with the free Alpaca API - you can't received last 1 hour date
        # That's why we initialize the bot with no bars
        self._init_state()

    def _init_state(self):
        orders = self._core.list_orders(status="open")
        for order in orders:
            self._core.cancel_order(order.id)

        self._order = None
        self._position = None
        self._state = 'TO_BUY'

    def _submit_buy(self):
        trade = self._core.get_last_trade(self._symbol)
        amount = int(self._lot / trade.price)
        try:
            order = self._core.submit_order(
                symbol=self._symbol,
                side='buy',
                type='limit',
                qty=amount,
                time_in_force='day',
                limit_price=trade.price,
            )
        except Exception as ex:
            print(ex)
            self._transition('TO_BUY')
        
        else:
            self._order = order
            print(f'submitted buy {order}')
            self._transition('BUY_SUBMITTED')

    def _submit_sell(self, bailout=False):
        params = dict(
            symbol=self._symbol,
            side='sell',
            qty=self._position.qty,
            time_in_force='day',
        )
        if bailout:
            params['type'] = 'market'
        else:
            current_price = float(self._core.get_last_trade(self._symbol).price)
            cost_basis = float(self._position.avg_entry_price)
            limit_price = max(cost_basis + 0.01, current_price)
            params.update(dict(
                type='limit',
                limit_price=limit_price,
            ))
        try:
            order = self._core.submit_order(**params)
        except Exception as ex:
            print(ex)
            self._transition('TO_SELL')

        else:
            self._order = order
            print(f'submitted sell {order}')
            self._transition('SELL_SUBMITTED')

    def _transition(self, new_state):
        print(f'transition from {self._state} to {new_state}')
        self._state = new_state

    def _calc_buy_signal(self):
        mavg = self._bars.rolling(3).mean().close.values
        closes = self._bars.close.values
        if closes[-2] < mavg[-2] and closes[-1] > mavg[-1]:
            print(f'buy signal: closes[-2] {closes[-2]} < mavg[-2] {mavg[-2]}',
                  f'closes[-1] {closes[-1]} > mavg[-1] {mavg[-1]}')
            return True
        else:
            print(f'closes[-2:] = {closes[-2:]}, mavg[-2:] = {mavg[-2:]}')
            return False

    def _outofmarket(self):
        return self._core.now() >= self._next_close

    def _cancel_order(self):
        if self._order is not None:
            self._core.cancel_order(self._order.id)

    def on_bar(self, bar):
        self._bars = self._bars.append(pd.DataFrame({
            'open': bar.open, 'high': bar.high, 'low': bar.low, 'close': bar.close,
            'volume': bar.volume}, index=[bar.timestamp])
        )

        print(f'received bar start = {bar.timestamp}, close = {bar.close}, len(bars) = {len(self._bars)}')
        if len(self._bars) < 4:
            return
        if self._outofmarket():
            return
        if self._state == 'TO_BUY':
            if self._calc_buy_signal():
                self._submit_buy()

    def on_order_update(self, event, data):
        print(f'order update: {event} = {order}')
        if event == 'fill':
            self._order = None
            if self._state == 'BUY_SUBMITTED':
                self._position = self._core.get_position(self._symbol)
                self._transition('TO_SELL')
                self._submit_sell()
                return
            elif self._state == 'SELL_SUBMITTED':
                self._position = None
                self._transition('TO_BUY')
                return
        elif event == 'partial_fill':
            self._position = self._core.get_position(self._symbol)
            self._order = self._core.get_order(order['id'])
        elif event in ('canceled', 'rejected'):
            if event == 'rejected':
                print(f'order rejected: current order = {self._order}')
            self._order = None
            if self._state == 'BUY_SUBMITTED':
                if self._position is not None:
                    self._transition('TO_SELL')
                    self._submit_sell()
                else:
                    self._transition('TO_BUY')
            elif self._state == 'SELL_SUBMITTED':
                self._transition('TO_SELL')
                self._submit_sell(bailout=True)
            else:
                print(f'unexpected state for {event}: {self._state}')

    def on_position(self, position):
        now = self._core.now()
        order = self._order
        print(order)
        if (order is not None and order.side == 'buy' and now -
                pd.Timestamp(order.submitted_at, tz='America/New_York') > pd.Timedelta('2 min')):
            last_price = self._api.get_last_trade(self._symbol).price
            print(f'canceling missed buy order {order.id} at {order.limit_price}',
                  f'(current price = {last_price})')
            self._cancel_order()

        if self._position is not None and self._outofmarket():
            self._submit_sell(bailout=True)


class ScalpStrategy:
    def __init__(self, portfolio : Portfolio):
        self.core = core = portfolio.get_core()

        self.algo_pile = {x : ScalpAlgo(core, x) for x in portfolio.get_symbols()}
        self.stream = stream = core.create_new_stream()

        stream.subscribe_bars(self.on_bars_async, *portfolio.get_symbols())
        stream.subscribe_trade_updates(self.on_orders_update_async)

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(asyncio.gather(
                self.stream._run_forever(),
                self.loop_positions(),
            ))
        except Exception as ex:
            print('Finishing strategy because of ex:', ex)

        loop.close()

    async def loop_positions(self):
        starttime = time.time()
        while True:
            print('loop_orders called')
            if not self.core.is_market_open():
                print('Exiting from strategy: market is not open')
                await self.stream.stop_ws()
                break

            await asyncio.sleep(30 - (time.time() - starttime) % 30)
            positions = self.core.list_positions()
            for symbol, algo in self.algo_pile.items():
                pos = [p for p in positions if p.symbol == symbol]
                algo.on_position(pos[0] if len(pos) > 0 else None)

    async def on_bars_async(self, data):
        print('Received:', data)
        if data.symbol in self.algo_pile:
            self.algo_pile[data.symbol].on_bar(data)

    async def on_orders_update_async(self, data):
        print('Received:', data)
        if data.symbol in self.algo_pile:
            self.algo_pile[symbol].on_order_update(data.event, data.order)