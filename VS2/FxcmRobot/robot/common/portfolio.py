from .trade import Trade

class TradeShortcut:
    def __init__(self, **args):
        self.__dict__.update(args)

    def create_trade(self, **args):
        args.update(self.__dict__)
        return Trade(**args)

    def get_args(self):
        return self.__dict__


class Portfolio:
    def __init__(self, symbols, pile_size, risk_rate = 0.03, coefs = None):
        self.symbols = set(symbols)

        if not coefs: coefs = [1/len(symbols) for _ in range(len(symbols))]

        self.risk_rate = risk_rate
        self.pile_sizes = {sym : pile_size * coefs[i] for i, sym in enumerate(symbols)}

        self.trade_shortcuts = {}

    def get_lot_size(self, symbol):
        pile_size = self.pile_sizes.get(symbol, None)
        return pile_size * self.risk_rate if pile_size else None

    def create_trade_shortcut(self, id, **args):
        shortcut = TradeShortcut(**args)
        self.trade_shortcuts[id] = shortcut
        return shortcut

    def create_trade(self, shortcut_id, **args):
        s = self.trade_shortcuts.get(shortcut_id, None)
        return s.create_trade(**args) if s else None

    def get_shortcut(self, shortcut_id):
        return self.trade_shortcuts.get(shortcut_id, None)

    def get_symbols(self):
        return self.symbols

