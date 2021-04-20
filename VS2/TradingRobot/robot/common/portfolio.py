
class Portfolio:
    def __init__(self, core, symbols, pile_size, risk_rate):
        self.core = core
        self.symbols = set(symbols)

        self.pile_size = pile_size
        self.risk_rate = risk_rate
        self.lot_size = pile_size * risk_rate

    def get_core(self):
        return self.core

    def get_symbols(self):
        return self.symbols
