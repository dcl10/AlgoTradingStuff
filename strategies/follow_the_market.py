import sys
import configparser
from api_models.models import get_account, Account
from backtest.backtest import BackTester

oanda_config = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]
instrument = sys.argv[4]

parser = configparser.ConfigParser()
parser.read(oanda_config)

api_key = parser.get('oanda', 'api_key')
account_id = parser.get('oanda', 'primary_account')
base_url = parser.get('oanda', 'base_url')

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

