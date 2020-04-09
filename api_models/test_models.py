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
        self.account = Account(self.api_key, self.base_url, self.account_id, **acc)

    def tearDown(self) -> None:
        close_req = requests.put(f'{self.base_url}/accounts/{self.account_id}/positions/GBP_USD/close',
                                 headers={'Authorization': f'Bearer {self.api_key}',
                                          'Content-Type': 'application/json'},
                                 data=json.dumps({'longUnits': "ALL"}))
        close_req.close()

    def test_create_order(self):
        new_order = {'order': {'type': 'MARKET',
                               'units': '1',
                               'timeInForce': 'FOK',
                               'instrument': 'GBP_USD',
                               'positionFill': 'DEFAULT'}}
        order_response = self.account.create_order(new_order)
        self.assertIsInstance(order_response, dict)

    def test_cancel_order(self):
        data = {'order': {"price": '1.2',
                          "timeInForce": "GTC",
                          "instrument": "GBP_USD",
                          "units": "1",
                          "clientExtensions": {
                              "comment": "New idea for trading",
                              "tag": "strategy_9",
                              "id": "my_order_100"
                          },
                          "type": "MARKET_IF_TOUCHED",
                          "positionFill": "DEFAULT"}}
        orders_req = requests.post(f'{self.base_url}/accounts/{self.account_id}/orders',
                                   json=data,
                                   headers={'Authorization': f'Bearer {self.api_key}'})
        order_id = orders_req.json().get('orderCreateTransaction').get('id')
        orders_req.close()
        result = self.account.cancel_order(order_id)
        self.assertIsInstance(result, dict)

    def test_get_open_positions(self):
        self.assertEqual(self.account.get_open_positions(), [])
        new_order = {'order': {'type': 'MARKET',
                               'units': '1',
                               'timeInForce': 'FOK',
                               'instrument': 'GBP_USD',
                               'positionFill': 'DEFAULT'}}
        order_req = requests.post(f'{self.base_url}/accounts/{self.account_id}/orders',
                                  json=new_order,
                                  headers={'Authorization': f'Bearer {self.api_key}'})
        order_req.close()
        positions = self.account.get_open_positions()
        self.assertIsInstance(positions, list)
        self.assertIsInstance(positions[0], dict)
        close_req = requests.put(f'{self.base_url}/accounts/{self.account_id}/positions/{positions[0].get("instrument")}/close',
                                 headers={'Authorization': f'Bearer {self.api_key}',
                                          'Content-Type': 'application/json'},
                                 data=json.dumps({'longUnits': "ALL"}))
        close_req.close()

    def test_close_position(self):
        new_order = {'order': {'type': 'MARKET',
                               'units': '1',
                               'timeInForce': 'FOK',
                               'instrument': 'GBP_USD',
                               'positionFill': 'DEFAULT'}}
        order_req = requests.post(f'{self.base_url}/accounts/{self.account_id}/orders',
                                  json=new_order,
                                  headers={'Authorization': f'Bearer {self.api_key}'})
        order_req.close()
        self.assertIsInstance(self.account.close_position('GBP_USD'), dict)

    def test_get_open_trades(self):
        self.assertEqual(self.account.get_open_trades(), [])
        new_order = {'order': {'type': 'MARKET',
                               'units': '1',
                               'timeInForce': 'FOK',
                               'instrument': 'GBP_USD',
                               'positionFill': 'DEFAULT'}}
        order_req = requests.post(f'{self.base_url}/accounts/{self.account_id}/orders',
                                  json=new_order,
                                  headers={'Authorization': f'Bearer {self.api_key}'})
        order_req.close()
        trades = self.account.get_open_positions()
        self.assertIsInstance(trades, list)

    def test_close_trade(self):
        c_trade_req = self.account.close_trade('0000')
        self.assertIsInstance(c_trade_req, dict)

    def test_get_candles(self):
        candles = self.account.get_candles('GBP_USD',
                                           start=(dt.datetime.today() - dt.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                                           end=dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        self.assertIsInstance(candles, list)
        self.assertRaises(AssertionError, self.account.get_candles, 'GBP_USD',
                          start=str((dt.datetime.today() + dt.timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')),
                          end=str(dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')))


class TestStaticMethods(unittest.TestCase):

    def setUp(self) -> None:
        parser = configparser.ConfigParser()
        parser.read('oanda.txt')
        self.api_key = parser['oanda'].get('api_key')
        self.account = parser['oanda'].get('primary_account')

    def test_get_accounts(self):
        accounts = get_accounts(self.api_key)
        self.assertIsInstance(accounts, list)
        self.assertIsInstance(accounts[0], dict)
        self.assertIn('id', accounts[0].keys())
        self.assertRaises(AccountError, get_accounts, 'iiwfojwfjowsjfw')

    def test_get_account(self):
        account = get_account('101-004-12979612-001', self.api_key)
        self.assertIsInstance(account, dict)
        self.assertIn('balance', account.keys())
        self.assertRaises(AccountError, get_account, 'sifjowsefjwesfj', self.api_key)


class TestIntegration(unittest.TestCase):

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
        self.account = Account(self.api_key, self.base_url, self.account_id, **acc)

    def tearDown(self) -> None:
        close_req = requests.put(f'{self.base_url}/accounts/{self.account_id}/positions/GBP_USD/close',
                                 headers={'Authorization': f'Bearer {self.api_key}',
                                          'Content-Type': 'application/json'},
                                 data=json.dumps({'longUnits': "ALL"}))
        close_req.close()

    def test_create_order(self):
        # Test a valid order for one unit of GBP_USD
        valid_new_order = {'order': {'type': 'MARKET',
                                     'units': '1',
                                     'timeInForce': 'FOK',
                                     'instrument': 'GBP_USD',
                                     'positionFill': 'DEFAULT'}}
        order_response = self.account.create_order(valid_new_order)
        self.assertIn('units', order_response)
        # Test bad order with non-existent instrument 'USD_GBP'
        invalid_new_order = {'order': {'type': 'MARKET',
                                       'units': '1',
                                       'timeInForce': 'FOK',
                                       'instrument': 'USD_GBP',
                                       'positionFill': 'DEFAULT'}}
        bad_order_response = self.account.create_order(invalid_new_order)
        self.assertEqual({}, bad_order_response)

    def test_close_trade(self):
        valid_new_order = {'order': {'type': 'MARKET',
                                     'units': '1',
                                     'timeInForce': 'FOK',
                                     'instrument': 'GBP_USD',
                                     'positionFill': 'DEFAULT'}}
        order_response = self.account.create_order(valid_new_order)
        trades = self.account.get_open_trades()
        c_trade_req = self.account.close_trade(trades[0].get('id', '0000'))
        self.assertIn('tradeClose', c_trade_req)

    def test_get_open_positions(self):
        self.assertEqual(self.account.get_open_positions(), [])
        new_order = {'order': {'type': 'MARKET',
                               'units': '1',
                               'timeInForce': 'FOK',
                               'instrument': 'GBP_USD',
                               'positionFill': 'DEFAULT'}}
        order_req = requests.post(f'{self.base_url}/accounts/{self.account_id}/orders',
                                  json=new_order,
                                  headers={'Authorization': f'Bearer {self.api_key}'})
        order_req.close()
        positions = self.account.get_open_positions()
        self.assertIsInstance(positions, list)
        self.assertIsInstance(positions[0], dict)
        self.assertIn('instrument', positions[0].keys())
        self.assertIn('unrealizedPL', positions[0].keys())
        self.assertIn('long', positions[0].keys())
        self.assertIn('short', positions[0].keys())
        close_req = requests.put(f'{self.base_url}/accounts/{self.account_id}/positions/{positions[0].get("instrument")}/close',
                                 headers={'Authorization': f'Bearer {self.api_key}',
                                          'Content-Type': 'application/json'},
                                 data=json.dumps({'longUnits': "ALL"}))
        close_req.close()


if __name__ == '__main__':
    unittest.main()
