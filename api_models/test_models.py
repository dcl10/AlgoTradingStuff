import unittest
import configparser
from api_models.models import Account, get_accounts, get_account


class TestAccount(unittest.TestCase):

    def setUp(self) -> None:
        parser = configparser.ConfigParser()
        parser.read('./oanda_config.txt')
        self.api_key = parser['oanda'].get('api_key')

    def test_create_order(self):
        account = Account(self.api_key, )
        pass


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
        bad_key = get_accounts('jfjwjfwjfjwfj')
        self.assertEqual(bad_key, None)

    def test_get_account(self):
        pass


if __name__ == '__main__':
    unittest.main()
