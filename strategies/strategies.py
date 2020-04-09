import datetime as dt
from abc import ABC, abstractmethod

from api_models.models import Account


class BaseStrategy(ABC):

    def __init__(self, account: Account, granularity: str = 'D',
                 start_date: str = (dt.datetime.today() - dt.timedelta(days=60)).strftime('%Y-%m-%d %H:%M:%S')):
        self.account = account
        self.granularity = granularity
        self.start_date = start_date

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def generate_instructions(self):
        pass

    def _vals_from_candles(self, candles):
        vals = []
        for c in candles:
            if 'mid' in c.keys():
                vals.append(float(c.get('mid').get('c', 0.0)))
            elif 'bid' in c.keys():
                vals.append(float(c.get('bid').get('c', 0.0)))
            elif 'ask' in c.keys():
                vals.append(float(c.get('ask').get('c', 0.0)))
            else:
                vals.append(0.0)
        return vals


class FollowMarketStrategy(BaseStrategy):

    def generate_instructions(self):
        pass

    def run(self):
        pass
