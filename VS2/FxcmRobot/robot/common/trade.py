class Trade:
    def __init__(self, symbol = None, amount = None,
                 is_buy = False, is_in_pips = True, time_in_force = 'GTC',
                 order_type = 'AtMarket'):
        self.symbol = symbol
        self.amount = amount
        self.is_buy = is_buy
        self.is_in_pips = is_in_pips
        self.session = time_in_force
        self.order_type = order_type