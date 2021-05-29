from enum import Enum

class ProviderType(Enum):
    FXCM = 1
    CSV = 2
    YFINANCE = 3
    ALPHA_VINTAGE = 4


fxcm_key_path = 'E:/Programming/Trading/tokens/fxcm.txt'
alpha_vintage_key_path = 'E:/Programming/Trading/tokens/alpha_vintage.txt'

from .fxcm_wrapper import FxcmAPI
from .csv_wrapper import CsvAPI
from .yfinance_wrapper import YFinanceAPI
from .alpha_vintage_wrapper import AlphaVintageAPI

def get_data_provider(type):
    if type == ProviderType.FXCM:
        token = open(fxcm_key_path, 'r').read()
        return FxcmAPI(token)
    elif type == ProviderType.CSV:
        return CsvAPI()
    elif type == ProviderType.YFINANCE:
        return YFinanceAPI()
    elif type == ProviderType.ALPHA_VINTAGE:
        token = open(alpha_vintage_key_path, 'r').read()
        return AlphaVintageAPI(token)