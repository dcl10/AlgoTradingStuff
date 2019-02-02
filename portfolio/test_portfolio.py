import unittest

from .portfolio import Portfolio, BaseHolding


class TestPortfolio(unittest.TestCase):

    def setUp(self):
        self.portfolio = Portfolio('MyPortfolio', 1000)

    def tearDown(self):
        del self.portfolio


class TestBaseHolding(unittest.TestCase):

    def setUp(self):
        self.holding = BaseHolding('aapl', current_price=10, n_units=1000)

    def tearDown(self):
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
        self.assertRaises(TypeError, self.holding.buy, n_units=0.0)

    def test_buy_amount(self):
        self.holding.buy(amount=1000)
        self.assertEqual(1000 + (1000 / self.holding.current_price), self.holding.n_units)
        self.assertRaises(TypeError, self.holding.buy, amount=0.0)

    def test_sell_units(self):
        self.holding.sell(n_units=500)
        self.assertEqual(500, self.holding.n_units)
        self.assertRaises(TypeError, self.holding.buy, n_units=0.0)

    def test_sell_amount(self):
        self.holding.sell(amount=1000)
        self.assertEqual(1000 - (1000 / self.holding.current_price), self.holding.n_units)
        self.assertRaises(TypeError, self.holding.buy, amount=0.0)

    def test_current_balance(self):
        self.assertEqual(1000 * 10, self.holding.balance)
