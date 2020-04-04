import sys
import configparser
import argparse
import datetime as dt
from api_models.models import get_account, Account
from backtest.backtest import BackTester

a_parser = argparse.ArgumentParser()
a_parser.add_argument('config', help='configuration file')
a_parser.add_argument('-s', '--start', dest='start', help='start date for the back test period',
                      default=(dt.datetime.today() - dt.timedelta(days=60)).strftime('%Y-%m-%d %H:%M:%S'))
a_parser.add_argument('-e', '--end', dest='end', help='end date for the back test period',
                      default=dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
a_parser.add_argument('-i', '--instrument', dest='instrument', help='the instrument to back test', default='GBP_USD')

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

candles = account.get_candles(instrument, start=start_date, end=end_date, granularity='W')

prices = []
for c in candles:
    prices.append(float(c.get('mid').get('o')))
instructions = [1]
for i in range(1, len(prices)):
    if prices[i] > prices[i - 1]:
        instructions.append(1)
    else:
        instructions.append(0)

bt = BackTester(float(account.balance), instructions, prices, margin=0.01)
bt.run()
print(f'{bt.result - bt.balance:n}')

