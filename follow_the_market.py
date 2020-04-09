import sys
import configparser
import argparse
import datetime as dt
from api_models.models import get_account, Account
from backtest.backtest import BackTester
from strategies.strategies import FollowMarketStrategy, vals_from_candles


a_parser = argparse.ArgumentParser()
a_parser.add_argument('config', help='configuration file')
a_parser.add_argument('-s', '--start', dest='start', help='start date for the back test period',
                      default=(dt.datetime.today() - dt.timedelta(days=60)).strftime('%Y-%m-%d %H:%M:%S'))
a_parser.add_argument('-e', '--end', dest='end', help='end date for the back test period',
                      default=dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
a_parser.add_argument('-i', '--instrument', dest='instrument', help='the instrument to back test', default='GBP_USD')



bt = BackTester(float(account.balance), instructions, prices, margin=0.01)
bt.run()
print(f'{bt.result - bt.balance:n}')

if __name__ == '__main__':
    args = a_parser.parse_args(sys.argv[1:])

    oanda_config = args.config
    start_date = args.start
    end_date = args.end
    instrument = args.instrument

    c_parser = configparser.ConfigParser()
    c_parser.read(oanda_config)

    api_key = c_parser.get('oanda', 'api_key')
    account_id = c_parser.get('oanda', 'primary_account')
    base_url = c_parser.get('oanda', 'base_url')

    oanda_account = get_account(base_url=base_url, api_key=api_key, account_id=account_id)
    account = Account(base_url=base_url, account_id=account_id, api_key=api_key, **oanda_account)

    mid_candles = account.get_candles(instrument, start=start_date, end=end_date, granularity='D')
    bid_candles = account.get_candles(instrument, start=start_date, end=end_date, granularity='D', price='B')
    ask_candles = account.get_candles(instrument, start=start_date, end=end_date, granularity='D', price='A')

    mid_prices = vals_from_candles(mid_candles)
    bid_prices = vals_from_candles(bid_candles)
    ask_prices = vals_from_candles(ask_candles)

    instructions = [1]
    prices = [bid_prices[0]]
    for i in range(1, len(mid_prices)):
        if mid_prices[i] > mid_prices[i - 1]:
            instructions.append(1)
            prices.append(bid_prices[i])
        else:
            instructions.append(0)
            prices.append(ask_prices[i])

