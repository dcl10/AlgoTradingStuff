import unittest
import configparser
import requests
from api_models.models import Account, get_accounts, get_account
from api_models.errors import AccountError


class TestAccount(unittest.TestCase):

    def setUp(self) -> None:
        parser = configparser.ConfigParser()
        parser.read('oanda.txt')
        self.api_key = parser['oanda'].get('api_key')
        self.account_id = parser['oanda'].get('primary_account')
        self.base_url = parser['oanda'].get('base_url')

    def test_create_order(self):
        response = requests.get(f'{self.base_url}/accounts/{self.account_id}',
                                headers={'Authorization': f'Bearer {self.api_key}'})
        acc = response.json().get('account', {})
        response.close()
        account = Account(self.api_key, self.base_url, self.account_id, **acc)
        new_order = {'order': {'type': 'MARKET',
                               'units': '1',
                               'timeInForce': 'FOK',
                               'instrument': 'GBP_USD',
                               'positionFill': 'DEFAULT'}}
        order_response = account.create_order(new_order)
        self.assertIsInstance(order_response, dict)
        self.assertIn('orderID', order_response)
        self.assertIn('accountID', order_response)
        self.assertIn('instrument', order_response)
        self.assertRaises(AccountError, account.create_order, {})

    def test_cancel_order(self):
        data = {'order': {'type': 'MARKET',
                          'units': '1',
                          'timeInForce': 'FOK',
                          'instrument': 'GBP_USD',
                          'positionFill': 'DEFAULT'}}
        orders_req = requests.post(f'{self.base_url}/accounts/{self.account_id}/orders',
                            json=data,
                            headers={'Authorization': f'Bearer {self.api_key}'})
        order_id = orders_req.json().get('orderFillTransaction')
        print(order_id)
        orders_req.close()
        account_req = requests.get(f'{self.base_url}/accounts/{self.account_id}',
                                headers={'Authorization': f'Bearer {self.api_key}'})
        acc = account_req.json().get('account', {})
        account_req.close()
        account = Account(self.api_key, self.base_url, self.account_id, **acc)
        result = account.cancel_order(order_id)
        self.assertIsInstance(result, dict)
        self.assertIn('reason', result.keys())
        self.assertEqual(result['reason'], 'CLIENT_REQUEST')
        self.assertRaises(AccountError, account.cancel_order, 'jeijfiejf')


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


if __name__ == '__main__':
    unittest.main()
