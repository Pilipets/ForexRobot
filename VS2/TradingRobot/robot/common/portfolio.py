
class Portfolio:
    def __init__(self, core, symbols):
        self.core = core
        self.symbols = symbols

    def add_symbol(self, symbol):
        if symbol not in self.symbols:
            self.symbols.append(symbol)

    def get_core(self):
        return self.core

    def get_symbols(self):
        return self.symbols
