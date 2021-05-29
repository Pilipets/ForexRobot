from enum import Enum

class Trade:
    class Type(Enum):
        LONG = 0
        SHORT = 1

    def __init__(self, type, date, entry_price, take_profit, stop_loss, units):
        self.id = id(self)
        self.result = 0
        self.closed = False

        self.type = type
        self.date = date
        self.entry_price = entry_price
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.units = units

    def is_short(self):
        return self.type == Trade.Type.SHORT

    def is_long(self):
        return self.type == Trade.Type.LONG

    def close_if_profit(self, price):
        if self.is_short():
            if self.take_profit >= price:
                self.result = (self.entry_price - self.take_profit) * self.units
                self.closed = True

        elif self.is_long():
            if self.take_profit <= price:
                self.result = (self.take_profit - self.entry_price) * self.units
                self.closed = True

        return self.closed

    def close_if_loss(self, price):
        if self.is_short():
            if self.stop_loss <= price:
                self.result = (self.entry_price - self.stop_loss) * self.units
                self.closed = True

        elif self.is_long():
            if self.stop_loss >= price:
                self.result = (self.stop_loss - self.entry_price) * self.units
                self.closed = True

        return self.closed

    def update(self, price):
        if self.is_short():
            if self.stop_loss <= price:
                self.result = (self.entry_price - self.stop_loss) * self.units
                self.closed = True
            elif self.take_profit >= price:
                self.result = (self.entry_price - self.take_profit) * self.units
                self.closed = True

        elif self.is_long():
            if self.take_profit <= price:
                self.result = (self.take_profit - self.entry_price) * self.units
                self.closed = True
            elif self.stop_loss >= price:
                self.result = (self.stop_loss - self.entry_price) * self.units
                self.closed = True

    def close(self, price):
        self.result = (price - self.entry_price) * self.units
        self.closed = True