import fxcmpy
import pandas as pd
from robot.common import Portfolio
import time

class FxRobot:
    def __init__(self, config):
        self.api = fxcmpy.fxcmpy(
            access_token = config.access_token,
            server= config.server,
            log_level = config.log_level)

        self.strategies = {}

    def __del__(self):
        self.api.close()

    def get_last_bar(self, symbol, columns = ['asks'], period = 'm1', n = 1):
        bars : pd.DataFrame = self.api.get_candles(
            symbol, period = period, number = n, columns = columns)

        bars.rename(columns={
            "bidopen": "open", "bidclose": "close", "bidhigh": "high", "bighlow" : "low"},
            inplace=True
        )
        return bars

    def get_api(self):
        return self.api

    def run(self):
        starttime=time.time()
        run_until = time.time() + 60*60*1
        period = 30

        df = pd.DataFrame()
        while starttime <= run_until:
            try:
                print("passthrough at ", time.time())
                data = bot.get_last_bar('EUR/USD', period = 'm1', n = 1)
        
                if df.empty or df.iloc[-1].index != data.iloc[0].index:
                    df.append(data)
    
                time.sleep(period - (time.time() - starttime) % period)
            except KeyboardInterrupt:
                print('\n\nKeyboard exception received. Exiting.')
                exit()
        
