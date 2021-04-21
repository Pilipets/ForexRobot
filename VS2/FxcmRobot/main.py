from fxcmpy import fxcmpy
from robot import FxRobot, Config

from robot import RenkoMacdStrategy

def run_bot():
    config = Config.from_file("config/fxcm_config.ini")
    bot = FxRobot(config)
    api : fxcmpy = bot.get_api()

    data = api.get_candles('EUR/USD', period='m1', number=10)

    df = api.get_open_positions()
    df2 = api.get_summary()
    print(df)

import pandas as pd
import time
starttime=time.time()
run_until = time.time() + 60*60*1
period = 15

while starttime <= run_until:
    try:
        print("passthrough at ", time.time())
        time.sleep(period - (time.time() - starttime) % period)
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()