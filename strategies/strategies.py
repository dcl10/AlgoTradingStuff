import datetime as dt
from abc import ABC, abstractmethod

from api_models.models import Account


def vals_from_candles(candles):
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


class BaseStrategy(ABC):

    deltas = {'H1': dt.timedelta(hours=1), 'H6': dt.timedelta(hours=6), 'H12': dt.timedelta(hours=12),
              'D': dt.timedelta(days=1), 'W': dt.timedelta(weeks=1)}

    def __init__(self, account: Account, start_date: str, granularity: str = 'D',
                 close_date: str = (dt.datetime.today() + dt.timedelta(days=60)).strftime('%Y-%m-%d %H:%M:%S')):
        self.account = account
        self.granularity = granularity
        self.start_date = start_date
        self.close_date = dt.datetime.strptime(close_date, '%Y-%m-%d %H:%M:%S')

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def generate_instructions(self):
        pass


class FollowMarketStrategy(BaseStrategy):

    def generate_instructions(self):
        pass

    def run(self):
        while not dt.datetime.today() >= self.close_date:
            print('Please give instructions.')
        open_positions = self.account.get_open_positions()
        for op in open_positions:
            self.account.close_position(op.get('instrument', ''))
