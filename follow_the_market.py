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
                      default=(dt.datetime.today() - dt.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'))
a_parser.add_argument('-e', '--end', dest='end', help='end date for the back test period',
                      default=dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
a_parser.add_argument('-c', '--close', dest='close', help='the close date for the position',
                      default=(dt.datetime.today() + dt.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'))
a_parser.add_argument('-i', '--instrument', dest='instrument', help='the instrument to back test', default='GBP_USD')
a_parser.add_argument('-g', '--granularity', dest='granularity', help='the spacing between the candles', default='M1')


if __name__ == '__main__':
    args = a_parser.parse_args(sys.argv[1:])

    oanda_config = args.config
    start_date = args.start
    end_date = args.end
    close_date = args.close
    instrument = args.instrument
    granularity = args.granularity

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

    instructions = [1]
    prices = [bid_prices[0]]
    for i in range(1, len(mid_prices)):
        if mid_prices[i] > mid_prices[i - 1]:
            instructions.append(1)
            prices.append(ask_prices[i])
        else:
            instructions.append(0)
            prices.append(bid_prices[i])

    currency_pair = instrument.split('_')
    if account.currency == currency_pair[0]:
        balance = float(account.balance) * prices[-1]
    else:
        balance = float(account.balance)

    bt = BackTester(balance, instructions, prices, margin=0.01)
    run_irl = bt.run()
    print(f'Result of backtest: {currency_pair[1]} {(bt.result - bt.balance):.2f}')
    if run_irl:
        strat = FollowMarketStrategy(account=account, instrument=instrument, granularity=granularity,
                                     start_date=start_date,
                                     close_date=close_date)
        strat.run()

    if account.currency == currency_pair[0]:
        final_balance = float(account.balance) * prices[-1]
    else:
        final_balance = float(account.balance)
    print(f'Result of real trading: {currency_pair[1]} {(final_balance - balance):.2f}')
