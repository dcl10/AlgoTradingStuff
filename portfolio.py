import abc
import math


class Portfolio:
    """
    This class represents a portfolio of investments and is a container for instances of the BaseHolding class
    and its subclasses.

    Attributes:
        name (str): The name of the portfolio.
        holdings (dict): A dict containing all the holdings in the portfolio, retrievable by name.
        pot (float): The amount of money available to be allocated to holdings.
    """

    def __init__(self, name, pot=0.0):
        """
        The constructor method for the class.

        :param name: (str) The name of the portfolio.
        :param pot: (float) The initial amount of money in the portfolio (default = 0.0).
        """
        self.name = name
        self.holdings = {}
        self.pot = pot

    @property
    def current_value(self):
        """Returns the sum of balances of every holding in the portfolio."""
        return sum([h.balance for h in self.holdings])

    def add_holdings(self, *args, **kwargs):
        """
        Add a holding to the portfolio. This can be done by passing comma separated BaseHolding objects as parameters,
        or as comma separated keyword-BaseHolding pairs.
        :param args: (BaseHolding) Instances of BaseHolding.
        :param kwargs: (BaseHolding) Keyword-BaseHolding pairs (e.g. aapl=BaseHolding('aapl')
        :return:
        """
        if args:
            for arg in args:
                assert isinstance(arg, BaseHolding), 'You can only add instances of BaseHolding and its subclasses'
                self.holdings.update({arg.name: arg})
        if kwargs:
            for key, value in kwargs.items():
                assert isinstance(value, BaseHolding), 'You can only add instances of BaseHolding and its subclasses'
            self.holdings.update(**kwargs)

    def remove_holdings(self, *args):
        """
        Sell all units of a named holding and remove it from the portfolio.

        :param args: (str) Comma separated strings corresponding to the names of holdings in the portfolio.
        :return:
        """
        for arg in args:
            del self.holdings[arg]

    def allocate(self, holding, amount, buy_units=False):
        """
        Allocate funds in the pot to a holding.
        :param holding: (str) The name of the holding to buy.
        :param amount: (int, float) Either a number of units to buy or an amount of money to convert to units.
        :param buy_units: (bool) Is amount a number of units or an amount of money?
        :return:
        """
        if buy_units:
            assert self.pot >= (self.holdings[holding].current_price * amount), 'You cannot allocate more funds than ' \
                                                                                'are in your portfolio\'s pot'
            self.holdings[holding].buy(n_units=amount)
            self.pot -= (self.holdings[holding].current_price * amount)
        else:
            assert self.pot >= amount, 'You cannot allocate more funds than are in your portfolio\'s pot'
            self.holdings[holding].buy(amount=amount)
            self.pot -= amount

    def deallocate(self, holding, amount, sell_units=False):
        """
        Allocate funds in the pot to a holding.
        :param holding: (str) The name of the holding to sell.
        :param amount: (int, float) Either a number of units to sell or an amount of money to convert to units.
        :param sell_units: (bool) Is amount a number of units or an amount of money?
        :return:
        """
        if sell_units:
            self.holdings[holding].sell(n_units=amount)
            self.pot += (self.holdings[holding].current_price * amount)
        else:
            self.holdings[holding].sell(amount=amount)
            self.pot += amount


class BaseHolding(abc.ABC):

    def __init__(self, name, data, price_col, n_units=0.0):
        self.name = name
        self.n_units = n_units
        self.data = data
        self.current_price = self.data[price_col][-1]

    @property
    @abc.abstractmethod
    def balance(self):
        pass

    @abc.abstractmethod
    def buy(self, n_units=0, amount=0):
        pass

    @abc.abstractmethod
    def sell(self, n_units=0, amount=0):
        pass

    def update(self, new, price_col):
        self.data = new
        self.current_price = self.data.loc[-1:, price_col]


class ForexHolding(BaseHolding):
    """This class handles currency exchanges."""

    @property
    def balance(self):
        """Return the value of this holding in your native currency."""
        return self.n_units / self.current_price

    def buy(self, n_units=0, amount=0):
        """
        Buy foreign currency.

        :param n_units: (int, float) The amount of foreign currency (in that currency) to buy.
        :param amount: (int, float) The amount of native currency to convert to foreign currency.
        :raise ValueError: Raised if both n_units and amount are 0.0 (default values), else n_units takes priority.
        :return:
        """
        assert isinstance(n_units, (int, float)), 'n_units must be an int or a float'
        assert isinstance(amount, (int, float)), 'amount must be an int or a float'
        if n_units != 0.0:
            self.n_units += n_units
        elif amount != 0.0:
            self.n_units += (amount * self.current_price)
        else:
            raise ValueError('You must specify either the number of units (n_units) or the amount (amount) '
                             'that you wish to purchase.')

    def sell(self, n_units=0, amount=0):
        """
        Sell foreign currency.

        :param n_units: (int, float) The amount of foreign currency you wish to convert back.
        :param amount: (int, float) The amount of native you wish to buy back.
        :raise ValueError: Raised if both n_units and amount are 0.0 (default values), else n_units takes priority.
        :return:
        """
        assert isinstance(n_units, (int, float)), 'n_units must be an int or a float'
        assert isinstance(amount, (int, float)), 'amount must be an int or a float'
        if n_units != 0.0:
            self.n_units -= n_units
        elif amount != 0.0:
            self.n_units -= (amount * self.current_price)
        else:
            raise ValueError('You must specify either the number of units (n_units) or the amount (amount) '
                             'that you wish to sell.')


class ShareHolding(BaseHolding):

    def __init__(self, name, data, price_col, n_units=0.0):
        n_units = int(n_units)  # coerce n_units to int
        super().__init__(name, data, price_col, n_units=n_units)

    @property
    def balance(self):
        return self.n_units * self.current_price

    def buy(self, n_units=0, amount=0):
        """
        Buy shares.

        :param n_units: (int) The number of shares to buy.
        :param amount: (int, float) Buy a number of shares corresponding to an amount of money.
        :raise ValueError: Raised if both n_units and amount are 0.0 (default values), else n_units takes priority.
        :return:
        """
        assert isinstance(n_units, int), 'n_units must be an int'
        assert isinstance(amount, (int, float)), 'amount must be an int or a float'
        if n_units != 0.0:
            self.n_units += n_units
        elif amount != 0.0:
            self.n_units += math.floor((amount / self.current_price))
        else:
            raise ValueError('You must specify either the number of units (n_units) or the amount (amount) '
                             'that you wish to purchase.')

    def sell(self, n_units=0, amount=0):
        """
        Sell shares.

        :param n_units: (int) The number of shares to sell.
        :param amount: (int, float) Sell the number of shares corresponding to an amount of money.
        :raise ValueError: Raised if both n_units and amount are 0.0 (default values), else n_units takes priority.
        :return:
        """
        assert isinstance(n_units, int), 'n_units must be an int'
        assert isinstance(amount, (int, float)), 'amount must be an int or a float'
        if n_units != 0.0:
            self.n_units -= n_units
        elif amount != 0.0:
            self.n_units -= math.floor((amount / self.current_price))
        else:
            raise ValueError('You must specify either the number of units (n_units) or the amount (amount) '
                             'that you wish to sell.')


def make_holding(kind, name, data, price_col, n_units=0.0):
    """
    Factory method for making Holding objects.

    :param kind: (str) The kind of Holding you want to make ({'share', 'forex'})
    :param name: (str) The name of the Holding
    :param data: (pandas.DataFrame) Data table for the Holding
    :param price_col: (str) The name of the column with the price values
    :param n_units: (int, float) The number of units you want initially; coerced to int if kind == 'share'
    :return: BaseHolding subclass
    """
    if kind == 'share':
        return ShareHolding(name, data, price_col, n_units)
    elif kind == 'forex':
        return ForexHolding(name, data, price_col, n_units)
    else:
        raise ValueError('`kind` must be \'share\' or \'forex\'.')
