from .trade import Trade

class TradeShortcut(dict):
    def __init__(self, id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id

    def create_trade(self, **args):
        args.update(super().items())
        return Trade(**args)

    def get_args(self):
        return super().values()

    def __repr__(self):
        return f'{TradeShortcut.__name__}[{self.id}]({super().__repr__()})'


class BasePortfolio:
    def __init__(self, robot, symbols, pile_size, risk_rate = 0.03, coefs = None):
        self.robot = robot
        self.symbols = set(symbols)
        if not coefs: coefs = [1/len(symbols) for _ in range(len(symbols))]

        self.risk_rate = risk_rate
        self.pile_sizes = {sym : pile_size * coefs[i] for i, sym in enumerate(symbols)}
        self.lot_sizes = {sym : int(pile_size * self.risk_rate) for sym in symbols}
        self.__dict__['id'] = self.id

        self.trade_shortcuts = {}
        self.order_ids = set() 

    def add_order(self, order):
        # We need strings for group portfolio positions method
        if order: self.order_ids.add(str(order.get_orderId()))

    def get_lot_size(self, symbol):
        return self.lot_sizes.get(symbol, None)

    def create_trade_shortcut(self, id, **args):
        shortcut = TradeShortcut(id, **args)
        self.trade_shortcuts[id] = shortcut
        return shortcut

    def create_trade(self, shortcut_id, **args):
        s = self.trade_shortcuts.get(shortcut_id, None)
        return s.create_trade(**args) if s else None

    def get_shortcut(self, shortcut_id):
        return self.trade_shortcuts.get(shortcut_id, None)

    def get_order_ids(self):
        return self.order_ids

    def get_symbols(self):
        return self.symbols

    def __repr__(self):
        args = self.__dict__
        args['id'] = self.id
        return f'{self.__class__.__name__}({args})'

    @property
    def id(self):
        return id(self)

