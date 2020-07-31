import unittest
import configparser
import requests
import datetime as dt
from algotradingstuff.accounts import OandaAccount, get_accounts, get_account
from algotradingstuff.accounts import AccountError


class TestAccount(unittest.TestCase):

    def setUp(self) -> None:
        parser = configparser.ConfigParser()
        parser.read('oanda.txt')
        self.api_key = parser['oanda'].get('api_key')
        self.account_id = parser['oanda'].get('primary_account')
        self.base_url = parser['oanda'].get('base_url')
        response = requests.get(f'{self.base_url}/accounts/{self.account_id}',
                                headers={'Authorization': f'Bearer {self.api_key}'})
        acc = response.json().get('account', {})
        self.last_transaction = response.json().get('lastTransactionID', '')
        response.close()
        self.primary_account = OandaAccount(self.api_key, self.base_url, **acc)

    def test_create_order(self):
        new_order = {'order': {'type': 'MARKET',
                               'units': '100',
                               'timeInForce': 'FOK',
                               'instrument': 'GBP_USD',
                               'positionFill': 'DEFAULT'}}
        order_request = self.primary_account.create_order(new_order)
        self.assertIsInstance(order_request, requests.PreparedRequest)
        self.assertIn('Authorization', order_request.headers)
        self.assertIn('Content-Type', order_request.headers)
        self.assertEqual(order_request.headers['Authorization'], f'Bearer {self.api_key}')
        self.assertEqual(order_request.url, f'{self.base_url}/accounts/{self.account_id}/orders')
        self.assertEqual(order_request.method, 'POST')
        self.assertIn(b'order', order_request.body)
        self.assertIn(b'units', order_request.body)
        self.assertIn(b'100', order_request.body)
        self.assertIn(b'timeInForce', order_request.body)
        self.assertIn(b'FOK', order_request.body)
        self.assertIn(b'instrument', order_request.body)
        self.assertIn(b'GBP_USD', order_request.body)
        self.assertIn(b'positionFill', order_request.body)
        self.assertIn(b'DEFAULT', order_request.body)
        self.assertIn(b'type', order_request.body)
        self.assertIn(b'MARKET', order_request.body)

    def test_get_orders(self):
        order_request = self.primary_account.get_orders()
        self.assertIsInstance(order_request, requests.PreparedRequest)
        self.assertIn('Authorization', order_request.headers)
        self.assertIn('Content-Type', order_request.headers)
        self.assertEqual(order_request.headers['Authorization'], f'Bearer {self.api_key}')
        self.assertEqual(order_request.url, f'{self.base_url}/accounts/{self.account_id}/orders')
        self.assertEqual(order_request.method, 'GET')
        self.assertIsNone(order_request.body)

    def test_cancel_order(self):
        order_id = '6543'
        cancel_order_requests = self.primary_account.cancel_order(order_id)
        self.assertIsInstance(cancel_order_requests, requests.PreparedRequest)
        self.assertIn('Authorization', cancel_order_requests.headers)
        self.assertIn('Content-Type', cancel_order_requests.headers)
        self.assertEqual(cancel_order_requests.headers['Authorization'], f'Bearer {self.api_key}')
        self.assertEqual(cancel_order_requests.url,
                         f'{self.base_url}/accounts/{self.account_id}/orders/{order_id}/cancel')
        self.assertEqual(cancel_order_requests.method, 'PUT')
        self.assertIsNone(cancel_order_requests.body)

    def test_get_open_positions(self):
        positions_requests = self.primary_account.get_open_positions()
        self.assertIsInstance(positions_requests, requests.PreparedRequest)
        self.assertIn('Authorization', positions_requests.headers)
        self.assertIn('Content-Type', positions_requests.headers)
        self.assertEqual(positions_requests.headers['Authorization'], f'Bearer {self.api_key}')
        self.assertEqual(positions_requests.url, f'{self.base_url}/accounts/{self.account_id}/openPositions')
        self.assertEqual(positions_requests.method, 'GET')
        self.assertIsNone(positions_requests.body)

    def test_close_position(self):
        instrument = 'GBP_USD'
        close_position_request = self.primary_account.close_position(instrument, long=True)
        self.assertIsInstance(close_position_request, requests.PreparedRequest)
        self.assertIn('Authorization', close_position_request.headers)
        self.assertIn('Content-Type', close_position_request.headers)
        self.assertEqual(close_position_request.headers['Authorization'], f'Bearer {self.api_key}')
        self.assertEqual(close_position_request.url,
                         f'{self.base_url}/accounts/{self.account_id}/positions/{instrument}/close')
        self.assertEqual(close_position_request.method, 'PUT')
        self.assertIn(b'longUnits', close_position_request.body)
        self.assertIn(b'ALL', close_position_request.body)

    def test_get_open_trades(self):
        trades_request = self.primary_account.get_open_trades()
        self.assertIsInstance(trades_request, requests.PreparedRequest)
        self.assertIn('Authorization', trades_request.headers)
        self.assertIn('Content-Type', trades_request.headers)
        self.assertEqual(trades_request.headers['Authorization'], f'Bearer {self.api_key}')
        self.assertEqual(trades_request.url, f'{self.base_url}/accounts/{self.account_id}/openTrades')
        self.assertEqual(trades_request.method, 'GET')
        self.assertIsNone(trades_request.body)

    def test_close_trade(self):
        trade_id = '1000'
        close_trade_request = self.primary_account.close_trade(trade_id)
        self.assertIsInstance(close_trade_request, requests.PreparedRequest)
        self.assertIn('Authorization', close_trade_request.headers)
        self.assertIn('Content-Type', close_trade_request.headers)
        self.assertEqual(close_trade_request.headers['Authorization'], f'Bearer {self.api_key}')
        self.assertEqual(close_trade_request.url,
                         f'{self.base_url}/accounts/{self.account_id}/trades/{trade_id}/close')
        self.assertEqual(close_trade_request.method, 'PUT')
        self.assertIsNone(close_trade_request.body)

    def test_get_candles(self):
        start = (dt.datetime.today() - dt.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        start_ts = str(dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timestamp())
        end = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        end_ts = str(dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S').timestamp())
        instrument = 'GBP_USD'
        count = 1
        candles_request = self.primary_account.get_candles(instrument,
                                                           start=start,
                                                           end=end)
        self.assertIsInstance(candles_request, requests.PreparedRequest)
        self.assertIn(start_ts, candles_request.url)
        self.assertIn(end_ts, candles_request.url)
        self.assertIn(instrument, candles_request.url)
        one_candle_request = self.primary_account.get_candles(instrument, count=count)
        self.assertIsInstance(one_candle_request, requests.PreparedRequest)
        self.assertIn(instrument, one_candle_request.url)
        self.assertNotIn('from', one_candle_request.url)
        self.assertNotIn('to', one_candle_request.url)

    def test_update_account_state(self):
        self.assertTrue(self.primary_account.update_account_state(self.last_transaction))
        self.assertRaises(AccountError, self.primary_account.update_account_state, '0000')


class TestStaticMethods(unittest.TestCase):

    def setUp(self) -> None:
        parser = configparser.ConfigParser()
        parser.read('oanda.txt')
        self.api_key = parser['oanda'].get('api_key')
        self.primary_account = parser['oanda'].get('primary_account')
        self.base_url = parser['oanda'].get('base_url')

    def test_get_accounts(self):
        accounts = get_accounts(self.api_key, self.base_url)
        self.assertIsInstance(accounts, list)
        self.assertIsInstance(accounts[0], OandaAccount)
        self.assertIn('id', accounts[0].__dict__)
        self.assertRaises(AccountError, get_accounts, 'iiwfojwfjowsjfw', self.base_url)

    def test_get_account(self):
        account = get_account(self.primary_account, self.api_key, self.base_url)
        self.assertIsInstance(account, OandaAccount)
        self.assertIn('balance', account.__dict__)
        self.assertRaises(AccountError, get_account, 'sifjowsefjwesfj', self.api_key, self.base_url)


if __name__ == '__main__':
    unittest.main()
