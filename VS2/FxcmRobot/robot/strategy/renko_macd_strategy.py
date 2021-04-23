from .base_strategy import BaseStrategy
from ..data_control import FrameClient
from ..common import indicators

class RenkoMacdStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def prepare_df(self, df):
        renko_df = indicators.RenkoDF(df) # df index is reset in the RenkoDF
        df = df.merge(renko_df.loc[:,["date", "bar_num"]], how="outer", on="date")

        df["bar_num"].fillna(method = 'ffill', inplace = True)
        df.set_index('date', inplace=True)

        client = FrameClient.from_df(self.fill_bricks(df))
        client.macd()
        client.slope('macd')
        client.slope('macd_signal')

        return client.get_df().dropna()

    def get_trades(self, df):
        print('Check get_trades called with', len(df), 'items')

        df = self.prepare_df(df)
        open_pos = con.get_open_positions()
        self.temp = df