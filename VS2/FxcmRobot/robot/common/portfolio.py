from collections import defaultdict

class Portfolio:
    def __init__(self, symbols, pile_size, risk_rate = None, coefs = None):
        self.symbols = set(symbols)

        if not risk_rate: risk_rate = 0.03
        if not coefs: coefs = [1/len(symbols) for _ in range(len(symbols))]

        self.risk_rate = risk_rate
        self.pile_sizes = {sym : pile_size * coefs[i] for i, sym in enumerate(symbols)}

        self.active_orders = defaultdict(dict)
        self.closed_orders = defaultdict(dict)
        self.positions = dict()

    def get_lot_size(self, symbol):
        pile_size = self.pile_sizes.get(symbol, None)
        return pile_size * self.risk_rate if pile_size else None

    def get_symbols(self):
        return self.symbols
