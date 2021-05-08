import copy

class Trade:
    def __init__(self, symbol=None, amount=None,
                 is_buy=False, is_in_pips=True,
                 time_in_force='GTC', stop=None,
                 trailing_step=None, order_type='AtMarket',
                 rate = 0):
        self.order_id = None

        self.symbol = symbol
        self.amount = amount
        self.rate = rate
        self.is_buy = is_buy
        self.is_in_pips = is_in_pips
        self.session = time_in_force
        self.order_type = order_type
        self.stop = stop
        self.trailing_step = trailing_step

    def set_order_id(self, id):
        self.order_id = id

    def get_order_id(self):
        return self.order_id

    def get_order_type(self):
        return self.order_type

    def get_fxcm_args(self):
        args = copy.copy(self.__dict__); del args['order_id']

        # Modifying names
        for x, y in [('session', 'time_in_force')]:
            args[y] = args.get(x, None)
            del args[x]
        
        return args

    def __repr__(self):
        return f'{Trade.__name__}({self.__dict__})'