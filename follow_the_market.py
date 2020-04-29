import sys
import configparser
import argparse
import datetime as dt
from api_models.models import get_account, Account
from backtest.backtest import BackTester
from strategies.strategies import FollowMarketStrategy, vals_from_candles, check_time


a_parser = argparse.ArgumentParser()
a_parser.add_argument('config', help='configuration file')
a_parser.add_argument('-s', '--start', dest='start', help='start date for the back test period',
                      default=(dt.datetime.today() - dt.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'))
a_parser.add_argument('-e', '--end', dest='end', help='end date for the back test period',
                      default=dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
a_parser.add_argument('-c', '--close', dest='close', help='the close date for the position',
                      default=(dt.datetime.today() + dt.timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S'))
a_parser.add_argument('-i', '--instrument', dest='instrument', help='the instrument to back test', default='GBP_USD')
a_parser.add_argument('-g', '--granularity', dest='granularity', help='the spacing between the candles', default='M1')
a_parser.add_argument('-m', '--margin', dest='margin', help='the fraction of your balance to risk on each trade',
                      default=0.01)

if __name__ == '__main__':
    args = a_parser.parse_args(sys.argv[1:])

    oanda_config = args.config
    start_date = args.start
    end_date = args.end
    close_date = args.close
    instrument = args.instrument
    granularity = args.granularity
    margin = args.margin

    c_parser = configparser.ConfigParser()
    c_parser.read(oanda_config)

    api_key = c_parser.get('oanda', 'api_key')
    account_id = c_parser.get('oanda', 'primary_account')
    base_url = c_parser.get('oanda', 'base_url')

    oanda_account = get_account(base_url=base_url, api_key=api_key, account_id=account_id)
    account = Account(base_url=base_url, account_id=account_id, api_key=api_key, **oanda_account)

    mid_candles = account.get_candles(instrument, start=start_date, end=end_date, granularity=granularity)
    bid_candles = account.get_candles(instrument, start=start_date, end=end_date, granularity=granularity, price='B')
    ask_candles = account.get_candles(instrument, start=start_date, end=end_date, granularity=granularity, price='A')

    mid_prices = vals_from_candles(mid_candles)
    bid_prices = vals_from_candles(bid_candles)
    ask_prices = vals_from_candles(ask_candles)

    instructions = [1, 0]
    prices = [ask_prices[0], bid_prices[-1]]
    currency_pair = instrument.split('_')
    if account.currency == currency_pair[0]:
        balance = float(account.balance) * prices[0]
        my_currency = currency_pair[0]
    else:
        balance = float(account.balance)
        my_currency = currency_pair[1]
    bt = BackTester(balance, instructions, prices, margin=margin)
    run_irl = bt.run()
    result = bt.result - bt.balance
    if account.currency == currency_pair[0]:
        result = result / bid_prices[-1]
    print(f'Result of backtest: {my_currency} {result}')
    print(f'Price at start: {currency_pair[1]} {ask_prices[0]} Price at end: {currency_pair[1]} {bid_prices[-1]}')

    if run_irl and check_time():
        strat = FollowMarketStrategy(account=account, instrument=instrument, granularity=granularity,
                                     close_date=close_date, margin=margin)
        strat.run()

    if account.currency == currency_pair[0]:
        final_balance = float(account.balance) * prices[0]
    else:
        final_balance = float(account.balance)

    print(f'Result of real trading: {my_currency} {final_balance - balance}')
