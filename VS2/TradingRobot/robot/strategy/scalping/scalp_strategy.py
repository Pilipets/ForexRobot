from ...common import Portfolio
from ...alpaca_internals import AlpacaCore

from alpaca_trade_api.rest import REST

import asyncio
import time
import pandas as pd

from .scalp_algo import ScalpAlgo

class ScalpStrategy:
    def __init__(self, portfolio : Portfolio, update_period):
        print('Initializing the scalping strategy on', portfolio.get_symbols())
        self.api: REST = portfolio.get_core().get_api()
        self.core: AlpacaCore = portfolio.get_core()
        self.portolio = portfolio

        # Configuration of the ScalpStrategy
        self.update_period = update_period

        today = self.core.now().floor('1min')
        today_str = today.strftime('%Y-%m-%d')
        calendar = self.api.get_calendar(start=today_str, end=today_str)[0]

        self.market_open = today.replace(
            hour=calendar.open.hour,
            minute=calendar.open.minute,
            second=0
        ) + pd.Timedelta('10min')

        self.market_close = today.replace(
            hour=calendar.close.hour,
            minute=calendar.close.minute,
            second=0
        ) - pd.Timedelta('10min')

        # ISSUE: This should be repetetive waiting till market is open in the loop
        if not self.market_open <= today <= self.market_close:
            print("Can't start the strategy as market is closed")
            return

        # Cancelling last portfolio symbol orders
        #symbols = portfolio.get_symbols()
        #cancel_orders = [r for r in self.api.list_orders(status="open", limit=500) if r.symbol in symbols]

        #print(f'Found {len(cancel_orders)} portfolio orders, cancelling all...')
        #for order in cancel_orders:
        #    self.api.cancel_order(order.id)

        self.algo_pile = {x : ScalpAlgo(portfolio.get_core(), x, portfolio.lot_size) for x in symbols}
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
            print('Loop over active positions callback called')
            if self.core.now() >= self.market_close:
                print('Exiting from ScalpStrategy: market is not open')
                await self.stream.stop_ws()

                # TODO: Close all ScalpAlgos
                break

            await asyncio.sleep(self.update_period - (time.time() - starttime) % self.update_period)
            positions = self.api.list_positions()
            for symbol, algo in self.algo_pile.items():
                pos = [x for x in positions if x.symbol == symbol]
                algo.checkup(pos[0] if pos else None)

    async def on_bars_async(self, data):
        if data.symbol in self.algo_pile:
            print('Received bar:', data)
            self.algo_pile[data.symbol].on_bar(data)

    async def on_orders_update_async(self, data):
        if data.symbol in self.algo_pile:
            print('Received order update:', data)
            self.algo_pile[symbol].on_order_update(data.event, data.order)