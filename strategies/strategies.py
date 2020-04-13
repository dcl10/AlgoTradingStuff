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

    deltas = {'M1': dt.timedelta(minutes=1), 'H1': dt.timedelta(hours=1), 'H6': dt.timedelta(hours=6),
              'H12': dt.timedelta(hours=12), 'D': dt.timedelta(days=1), 'W': dt.timedelta(weeks=1)}

    def __init__(self, account: Account, instrument: str, start_date: str, granularity: str = 'D',
                 close_date: str = (dt.datetime.today() + dt.timedelta(days=60)).strftime('%Y-%m-%d %H:%M:%S')):
        self.account = account
        self.granularity = granularity
        self.start_date = start_date
        self.instrument = instrument
        self.close_date = dt.datetime.strptime(close_date, '%Y-%m-%d %H:%M:%S')

    def _check_time(self, c_time: dt.datetime):
        is_weekday = 0 <= c_time.weekday() < 5
        is_trading_hours = dt.time(9, 0, 0) < c_time.time() < dt.time(17, 0, 0)
        return is_weekday and is_trading_hours

    @abstractmethod
    def run(self):
        pass


class FollowMarketStrategy(BaseStrategy):

    def run(self):
        balanace_at_start = float(self.account.balance)
        previous_time = dt.datetime.now()
        new_order = {'order': {'type': 'MARKET',
                               'units': '',
                               'timeInForce': 'FOK',
                               'instrument': self.instrument,
                               'positionFill': 'DEFAULT'}}
        while not dt.datetime.today() >= self.close_date:
            current_time = dt.datetime.now()
            if current_time >= previous_time + self.deltas[self.granularity] and self._check_time(current_time):
                print(f'Placing order at {current_time.strftime("%Y-%m-%d %H:%M:%S")}')
                open_trades = self.account.get_open_trades()
                for ot in open_trades:
                    self.account.close_trade(ot.get('id', ''))
                mid_candles = self.account.get_candles(self.instrument,
                                                       start=self.start_date,
                                                       end=current_time.strftime("%Y-%m-%d %H:%M:%S"), price='M',
                                                       granularity=self.granularity)
                mid_prices = vals_from_candles(mid_candles)
                if mid_prices[-1] > mid_prices[-2]:
                    new_order['order']['units'] = f'{-(0.01 * balanace_at_start):.2f}'  # negative units sells base currency
                    self.account.create_order(new_order)
                else:
                    new_order['order']['units'] = f'{(0.01 * balanace_at_start):.2f}'  # positive units buys base currency
                    self.account.create_order(new_order)
                previous_time = dt.datetime.now()

        open_positions = self.account.get_open_positions()
        for op in open_positions:
            self.account.close_position(op.get('instrument', ''))
