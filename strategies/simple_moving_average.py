import sys
import configparser
import argparse
import datetime as dt
import numpy as np
import pandas as pd
from api_models.models import get_account, Account
from backtest.backtest import BackTester


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

mid_candles = account.get_candles(instrument, start=start_date, end=end_date, granularity='H1')
bid_candles = account.get_candles(instrument, start=start_date, end=end_date, granularity='H1', price='B')
ask_candles = account.get_candles(instrument, start=start_date, end=end_date, granularity='H1', price='A')

mid_prices = vals_from_candles(mid_candles)
bid_prices = vals_from_candles(bid_candles)
ask_prices = vals_from_candles(ask_candles)

df = pd.DataFrame({'mid': mid_prices, 'bid': bid_prices, 'ask': ask_prices})
# Mid point prices
df['mid+3'] = df['mid'].rolling(3).mean()
df['mid+15'] = df['mid'].rolling(15).mean()
# Bid prices
df['bid+3'] = df['bid'].rolling(3).mean()
df['bid+15'] = df['bid'].rolling(15).mean()
# Ask prices
df['ask+3'] = df['ask'].rolling(3).mean()
df['ask+15'] = df['ask'].rolling(15).mean()
df.dropna(inplace=True)
df.reset_index(inplace=True)

instructions = [1]
prices = [df.loc[0, 'bid']]
for i in range(1, len(df)):
    if df.loc[i, 'mid+3'] > df.loc[i, 'mid+15']:
        prices.append(df.loc[i, 'bid'])
        instructions.append(1)
    else:
        prices.append(df.loc[i, 'ask'])
        instructions.append(0)

currency_pair = instrument.split('_')
if account.currency == currency_pair[0]:
    balance = float(account.balance) * prices[0]
else:
    balance = float(account.balance)
bt = BackTester(balance, instructions, prices, margin=0.01)
bt.run()
print(f'{currency_pair[1]} {bt.result - bt.balance:n}')
