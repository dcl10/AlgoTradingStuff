import datetime as dt
import time
import pandas as pd
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


def check_time():
    is_weekday = 0 <= dt.datetime.today().weekday() < 5
    return is_weekday


class BaseStrategy(ABC):

    deltas = {'M1': dt.timedelta(minutes=1), 'H1': dt.timedelta(hours=1), 'H6': dt.timedelta(hours=6),
              'H12': dt.timedelta(hours=12), 'D': dt.timedelta(days=1), 'W': dt.timedelta(weeks=1)}

    def __init__(self, account: Account, instrument: str, granularity: str = 'D',
                 close_date: str = (dt.datetime.today() + dt.timedelta(days=60)).strftime('%Y-%m-%d %H:%M:%S'),
                 margin: float = 0.01):
        self.account = account
        self.granularity = granularity
        self.instrument = instrument
        self.close_date = dt.datetime.strptime(close_date, '%Y-%m-%d %H:%M:%S')
        self.margin = margin

    @abstractmethod
    def run(self):
        pass


class FollowMarketStrategy(BaseStrategy):

    def run(self):
        balance_at_start = float(self.account.balance)
        new_order = {'order': {'type': 'MARKET',
                               'units': f'{int((self.margin * balance_at_start))}',
                               'timeInForce': 'FOK',
                               'instrument': self.instrument,
                               'positionFill': 'DEFAULT'}}
        self.account.create_order(new_order)
        while not dt.datetime.today() >= self.close_date:
            time.sleep(1)
        open_positions = self.account.get_open_positions()
        for op in open_positions:
            self.account.close_position(op.get('instrument', ''))


class CrossOverStrategy(BaseStrategy):

    def run(self):
        balance_at_start = float(self.account.balance)
        # new_order = {'order': {'type': 'MARKET',
        #                        'units': f'{int((self.margin * balance_at_start))}',
        #                        'timeInForce': 'FOK',
        #                        'instrument': self.instrument,
        #                        'positionFill': 'DEFAULT'}}
        # self.account.create_order(new_order)
        while not dt.datetime.today() >= self.close_date:
            # TODO: implement logic for crossover strategy
            bid_candles = self.account.get_candles(self.instrument, granularity=self.granularity, count=30, price='B')
            bid_prices = vals_from_candles(bid_candles)
            mid_candles = self.account.get_candles(self.instrument, granularity=self.granularity, count=30, price='M')
            mid_prices = vals_from_candles(mid_candles)
            ask_candles = self.account.get_candles(self.instrument, granularity=self.granularity, count=30, price='A')
            ask_prices = vals_from_candles(ask_candles)
            df = pd.DataFrame({'bid': bid_prices, 'mid': mid_prices, 'ask': ask_prices})
            df['mid+3'] = df['bid'].rolling(3).mean()
            df['mid+15'] = df['bid'].rolling(15).mean()
            df.dropna(inplace=True)
            df.reset_index(inplace=True, drop=True)
            print(df.tail())
            exit()
            pass
        # open_positions = self.account.get_open_positions()
        # for op in open_positions:
        #     self.account.close_position(op.get('instrument', ''))
