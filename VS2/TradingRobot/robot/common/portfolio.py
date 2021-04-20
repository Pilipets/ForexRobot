
class Portfolio:
    def __init__(self, core, symbols):
        self.core = core
        self.symbols = symbols

    def get_core(self):
        return self.core

    def get_symbols(self):
        return self.symbols
