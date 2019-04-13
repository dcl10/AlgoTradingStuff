import unittest
import math
import pandas as pd

from portfolio import Portfolio, ForexHolding, ShareHolding, make_holding


class TestPortfolio(unittest.TestCase):

    def setUp(self):
        self.portfolio = Portfolio('MyPortfolio', pot=1000)
        self.aapl = pd.read_csv('aapl_test.csv', index_col='Date')
        self.price = self.aapl['Adj_Close'][-1]

    def tearDown(self):
        del self.portfolio

    def test_add_remove(self):
        self.portfolio.add_holdings(ForexHolding('aapl', self.aapl, 'Adj_Close'))
        self.assertEqual(1, len(self.portfolio.holdings))
        self.assertRaises(AssertionError, self.portfolio.add_holdings, 1, 'hi', True, {'key': 'value'})
        self.portfolio.add_holdings(**{'msft': ForexHolding('msft', self.aapl, 'Adj_Close')})
        self.assertEqual(2, len(self.portfolio.holdings))
        self.portfolio.remove_holdings('aapl')
        self.assertEqual(1, len(self.portfolio.holdings))
        self.assertRaises(KeyError, self.portfolio.remove_holdings, 'tesla')

    def test_allocate(self):
        self.portfolio.holdings.update({'aapl': ForexHolding('aapl', self.aapl, price_col='Adj_Close')})
        self.portfolio.allocate('aapl', 100)
        self.assertEqual(self.portfolio.holdings['aapl'].n_units / self.price, self.portfolio.holdings['aapl'].balance)
        self.assertEqual(900, self.portfolio.pot)
        self.assertRaises(AssertionError, self.portfolio.allocate, 'aapl', 2000)

    def test_deallocate(self):
        self.portfolio.holdings.update({'aapl': ForexHolding('aapl', self.aapl, price_col='Adj_Close', n_units=100)})
        self.portfolio.deallocate('aapl', 500)
        self.assertEqual(1500, self.portfolio.pot)


class TestForexHolding(unittest.TestCase):

    def setUp(self):
        self.aapl = pd.read_csv('aapl_test.csv', index_col='Date')
        self.price = self.aapl['Adj_Close'][-1]
        self.holding = ForexHolding('aapl', self.aapl, price_col='Adj_Close', n_units=1000)

    def tearDown(self):
        del self.aapl
        del self.price
        del self.holding

    def test_buy_error(self):
        self.assertRaises(AssertionError, self.holding.buy, n_units='hi')
        self.assertRaises(AssertionError, self.holding.buy, amount='hi')

    def test_sell_error(self):
        self.assertRaises(AssertionError, self.holding.sell, n_units='hi')
        self.assertRaises(AssertionError, self.holding.sell, amount='hi')

    def test_buy_units(self):
        self.holding.buy(n_units=1000)
        self.assertEqual(2000, self.holding.n_units)
        self.assertRaises(ValueError, self.holding.buy, n_units=0.0)

    def test_buy_amount(self):
        self.holding.buy(amount=1000)
        self.assertEqual(1000 + (1000 * self.holding.current_price), self.holding.n_units)
        self.assertRaises(ValueError, self.holding.buy, amount=0.0)

    def test_sell_units(self):
        self.holding.sell(n_units=500)
        self.assertEqual(500, self.holding.n_units)
        self.assertRaises(ValueError, self.holding.buy, n_units=0.0)

    def test_sell_amount(self):
        self.holding.sell(amount=1000)
        self.assertEqual(1000 - (1000 * self.holding.current_price), self.holding.n_units)
        self.assertRaises(ValueError, self.holding.buy, amount=0.0)

    def test_current_balance(self):
        self.assertEqual(1000 / self.price, self.holding.balance)


class TestShareHolding(unittest.TestCase):

    def setUp(self):
        self.aapl = pd.read_csv('aapl_test.csv', index_col='Date').iloc[:-2, :]
        self.price = self.aapl['Adj_Close'][-1]
        self.holding = ShareHolding('aapl', self.aapl, price_col='Adj_Close', n_units=1000)

    def tearDown(self):
        del self.aapl
        del self.price
        del self.holding

    def test_buy_error(self):
        self.assertRaises(AssertionError, self.holding.buy, n_units='hi')
        self.assertRaises(AssertionError, self.holding.buy, amount='hi')

    def test_sell_error(self):
        self.assertRaises(AssertionError, self.holding.sell, n_units='hi')
        self.assertRaises(AssertionError, self.holding.sell, amount='hi')

    def test_buy_units(self):
        self.holding.buy(n_units=1000)
        self.assertEqual(2000, self.holding.n_units)
        self.assertRaises(ValueError, self.holding.buy, n_units=0)

    def test_buy_amount(self):
        self.holding.buy(amount=1000)
        self.assertEqual(math.floor(1000 + (1000 / self.holding.current_price)), self.holding.n_units)
        self.assertRaises(ValueError, self.holding.buy, amount=0.0)

    def test_sell_units(self):
        self.holding.sell(n_units=500)
        self.assertEqual(500, self.holding.n_units)
        self.assertRaises(ValueError, self.holding.buy, n_units=0)

    def test_sell_amount(self):
        self.holding.sell(amount=1000)
        self.assertEqual(math.ceil(1000 - (1000 / self.holding.current_price)), self.holding.n_units)
        self.assertRaises(ValueError, self.holding.buy, amount=0.0)

    def test_current_balance(self):
        self.assertEqual(1000 * self.price, self.holding.balance)


class TestHoldingFactory(unittest.TestCase):

    def setUp(self):
        self.aapl = pd.read_csv('aapl_test.csv', index_col='Date')

    def test_factory(self):
        share_test = make_holding('share', 'aapl', self.aapl, 'Adj_Close')
        self.assertIsInstance(share_test, ShareHolding)
        forex_test = make_holding('forex', 'aapl', self.aapl, 'Adj_Close')
        self.assertIsInstance(forex_test, ForexHolding)
        self.assertRaises(ValueError, make_holding, 'na', 'aapl', self.aapl, 'Adj_Close')
