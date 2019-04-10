import unittest

from portfolio import Portfolio, ForexHolding


class TestPortfolio(unittest.TestCase):

    def setUp(self):
        self.portfolio = Portfolio('MyPortfolio', pot=1000)

    def tearDown(self):
        del self.portfolio

    def test_add_remove(self):
        self.portfolio.add_holdings(ForexHolding('aapl', 10, 100))
        self.assertEqual(1, len(self.portfolio.holdings))
        self.assertRaises(AssertionError, self.portfolio.add_holdings, 1, 'hi', True, {'key': 'value'})
        self.portfolio.add_holdings(**{'msft': ForexHolding('msft', 10, 5)})
        self.assertEqual(2, len(self.portfolio.holdings))
        self.portfolio.remove_holdings('aapl')
        self.assertEqual(1, len(self.portfolio.holdings))
        self.assertRaises(KeyError, self.portfolio.remove_holdings, 'tesla')

    def test_allocate(self):
        self.portfolio.holdings.update({'aapl': ForexHolding('aapl', current_price=10)})
        self.portfolio.allocate('aapl', 100)
        self.assertEqual(100, self.portfolio.holdings['aapl'].balance)
        self.assertEqual(900, self.portfolio.pot)
        self.assertRaises(AssertionError, self.portfolio.allocate, 'aapl', 2000)

    def test_deallocate(self):
        self.portfolio.holdings.update({'aapl': ForexHolding('aapl', current_price=10, n_units=100)})
        self.portfolio.deallocate('aapl', 500)
        self.assertEqual(1500, self.portfolio.pot)


class TestForexHolding(unittest.TestCase):

    def setUp(self):
        self.holding = ForexHolding('aapl', current_price=10, n_units=1000)

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
        self.assertEqual(1000 / 10, self.holding.balance)
