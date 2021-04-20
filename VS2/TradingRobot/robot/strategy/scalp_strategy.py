from ..common import Portfolio

import asyncio

class ScalpAlgo:
    def __init__(self, symbol, core):
        self.symbol = symbol
        self.core = core

    def on_bar(self, data):
        pass

    def on_order_update(self, event, data):
        pass


class ScalpStrategy:
    def __init__(self, portfolio : Portfolio):
        core = portfolio.get_core()

        algo_pile = {x : ScalpAlgo(x, core) for x in portfolio.get_symbols()}
        stream = core.create_new_stream()

        stream.subscribe_bars(self.on_bars_async, *portfolio.get_symbols())
        stream.subscribe_trade_updates(self.on_orders_update_async)

    async def on_bars_async(data):
        print(data)
        if data.symbol in algo_pile:
            algo_pile[data.symbol].on_bar(data)

    async def on_orders_update_async(data):
        print(data)
        if data.symbol in algo_pile:
            algo_pile[symbol].on_order_update(data.event, data.order)