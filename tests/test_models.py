import unittest
import configparser
import requests
import json
import datetime as dt
from api_models.models import Account, get_accounts, get_account
from api_models.errors import AccountError


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
        response.close()
        self.primary_account = Account(self.api_key, self.base_url, **acc)

    def test_create_order(self):
        new_order = {'order': {'type': 'MARKET',
                               'units': '100',
                               'timeInForce': 'FOK',
                               'instrument': 'GBP_USD',
                               'positionFill': 'DEFAULT'}}
        order_response = self.primary_account.create_order(new_order)
        self.assertIsInstance(order_response, requests.PreparedRequest)
        self.assertIn('Authorization', order_response.headers)
        self.assertIn('Content-Type', order_response.headers)
        self.assertEqual(order_response.headers['Authorization'], f'Bearer {self.api_key}')
        self.assertEqual(order_response.url, f'{self.base_url}/accounts/{self.account_id}/orders')
        self.assertEqual(order_response.method, 'POST')
        self.assertIn(b'order', order_response.body)
        self.assertIn(b'units', order_response.body)
        self.assertIn(b'100', order_response.body)
        self.assertIn(b'timeInForce', order_response.body)
        self.assertIn(b'FOK', order_response.body)
        self.assertIn(b'instrument', order_response.body)
        self.assertIn(b'GBP_USD', order_response.body)
        self.assertIn(b'positionFill', order_response.body)
        self.assertIn(b'DEFAULT', order_response.body)
        self.assertIn(b'type', order_response.body)
        self.assertIn(b'MARKET', order_response.body)

    def test_get_orders(self):
        order_response = self.primary_account.get_orders()
        self.assertIsInstance(order_response, requests.PreparedRequest)
        self.assertIn('Authorization', order_response.headers)
        self.assertIn('Content-Type', order_response.headers)
        self.assertEqual(order_response.headers['Authorization'], f'Bearer {self.api_key}')
        self.assertEqual(order_response.url, f'{self.base_url}/accounts/{self.account_id}/orders')
        self.assertEqual(order_response.method, 'GET')
        self.assertIsNone(order_response.body)

    # def test_cancel_order(self):
    #     data = {'order': {"price": '1.2',
    #                       "timeInForce": "GTC",
    #                       "instrument": "GBP_USD",
    #                       "units": "1",
    #                       "clientExtensions": {
    #                           "comment": "New idea for trading",
    #                           "tag": "strategy_9",
    #                           "id": "my_order_100"
    #                       },
    #                       "type": "MARKET_IF_TOUCHED",
    #                       "positionFill": "DEFAULT"}}
    #     orders_req = requests.post(f'{self.base_url}/accounts/{self.account_id}/orders',
    #                                json=data,
    #                                headers={'Authorization': f'Bearer {self.api_key}'})
    #     order_id = orders_req.json().get('orderCreateTransaction').get('id')
    #     orders_req.close()
    #     result = self.primary_account.cancel_order(order_id)
    #     self.assertIsInstance(result, dict)
    #
    def test_get_open_positions(self):
        positions_response = self.primary_account.get_open_positions()
        self.assertIsInstance(positions_response, requests.PreparedRequest)
        self.assertIn('Authorization', positions_response.headers)
        self.assertIn('Content-Type', positions_response.headers)
        self.assertEqual(positions_response.headers['Authorization'], f'Bearer {self.api_key}')
        self.assertEqual(positions_response.url, f'{self.base_url}/accounts/{self.account_id}/openPositions')
        self.assertEqual(positions_response.method, 'GET')
        self.assertIsNone(positions_response.body)

    # def test_close_position(self):
    #     new_order = {'order': {'type': 'MARKET',
    #                            'units': '1',
    #                            'timeInForce': 'FOK',
    #                            'instrument': 'GBP_USD',
    #                            'positionFill': 'DEFAULT'}}
    #     order_req = requests.post(f'{self.base_url}/accounts/{self.account_id}/orders',
    #                               json=new_order,
    #                               headers={'Authorization': f'Bearer {self.api_key}'})
    #     order_req.close()
    #     self.assertIsInstance(self.primary_account.close_position('GBP_USD', True), dict)
    #
    def test_get_open_trades(self):
        trades_response = self.primary_account.get_open_trades()
        self.assertIsInstance(trades_response, requests.PreparedRequest)
        self.assertIn('Authorization', trades_response.headers)
        self.assertIn('Content-Type', trades_response.headers)
        self.assertEqual(trades_response.headers['Authorization'], f'Bearer {self.api_key}')
        self.assertEqual(trades_response.url, f'{self.base_url}/accounts/{self.account_id}/openTrades')
        self.assertEqual(trades_response.method, 'GET')
        self.assertIsNone(trades_response.body)

    # def test_close_trade(self):
    #     c_trade_req = self.primary_account.close_trade('0000')
    #     self.assertIsInstance(c_trade_req, dict)
    #
    # def test_get_candles(self):
    #     candles = self.primary_account.get_candles('GBP_USD',
    #                                        start=(dt.datetime.today() - dt.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
    #                                        end=dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    #     self.assertIsInstance(candles, list)
    #     one_candle = self.primary_account.get_candles('GBP_USD', count=1)
    #     self.assertEqual(len(one_candle), 1)


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
        self.assertIsInstance(accounts[0], Account)
        self.assertIn('id', accounts[0].__dict__)
        self.assertRaises(AccountError, get_accounts, 'iiwfojwfjowsjfw', self.base_url)

    def test_get_account(self):
        account = get_account(self.primary_account, self.api_key, self.base_url)
        self.assertIsInstance(account, Account)
        self.assertIn('balance', account.__dict__)
        self.assertRaises(AccountError, get_account, 'sifjowsefjwesfj', self.api_key, self.base_url)


if __name__ == '__main__':
    unittest.main()
