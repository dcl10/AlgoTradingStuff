import sys
import configparser
import argparse
import datetime as dt
import pandas as pd
from api_models.models import get_account, Account
from backtest.backtest import BackTester
from strategies.strategies import CrossOverStrategy, vals_from_candles, check_time


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
    df.reset_index(inplace=True, drop=True)

    currency_pair = instrument.split('_')
    instructions = [1]
    prices = [df.loc[0, 'ask']]
    for i in range(1, len(df)):
        if df.loc[i, 'mid+3'] > df.loc[i, 'mid+15'] and df.loc[i - 1, 'mid+3'] < df.loc[i - 1, 'mid+15']:
            prices.append(df.loc[i, 'bid'])
            instructions.append(0)
        elif df.loc[i, 'mid+3'] < df.loc[i, 'mid+15'] and df.loc[i - 1, 'mid+3'] > df.loc[i - 1, 'mid+15']:
            prices.append(df.loc[i, 'ask'])
            instructions.append(1)

    instructions.append(int(not instructions[-1]))
    if instructions[-1]:
        prices.append(ask_prices[-1])
    else:
        prices.append(bid_prices[-1])

    if account.currency == currency_pair[0]:
        prices = [1 / p for p in prices]

    balance = float(account.balance)
    bt = BackTester(balance, instructions, prices, margin=0.01)
    run_irl = bt.run()
    print(f'Result of backtest: {currency_pair[0]} {(bt.result - bt.balance)}')
    print(f'Price at start: {currency_pair[1]} {ask_prices[0]} Price at end: {currency_pair[1]} {bid_prices[-1]}')
    print(len(instructions))

    if run_irl and check_time():
        strat = CrossOverStrategy(account=account, instrument=instrument, granularity=granularity,
                                  close_date=close_date)
        strat.run()

    final_balance = float(account.balance)
    print(f'Result of real trading: {currency_pair[0]} {(final_balance - balance)}')
