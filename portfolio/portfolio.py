import abc


class Portfolio:

    def __init__(self, name, pot=0.0):
        self.name = name
        self.holdings = {}
        self.pot = pot

    @property
    def current_value(self):
        return sum([h.balance for h in self.holdings])

    def add_holdings(self, *args, **kwargs):
        if args:
            for arg in args:
                assert isinstance(arg, BaseHolding), 'You can only add instances of BaseHolding and its subclasses'
                self.holdings.update({arg.name: arg})
        if kwargs:
            self.holdings.update(**kwargs)

    def remove_holdings(self, *args):
        for arg in args:
            del self.holdings[arg]

    def allocate(self, holding, amount, buy_units=False):
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
        if sell_units:
            self.holdings[holding].sell(n_units=amount)
            self.pot += (self.holdings[holding].current_price * amount)
        else:
            self.holdings[holding].sell(amount=amount)
            self.pot += amount


class BaseHolding(abc.ABC):

    def __init__(self, name, n_units=0.0, current_price=0.0):
        self.name = name
        self.current_price = current_price
        self.n_units = n_units

    @property
    @abc.abstractmethod
    def balance(self):
        pass

    @abc.abstractmethod
    def buy(self, n_units=0.0, amount=0.0):
        pass

    @abc.abstractmethod
    def sell(self, n_units=0.0, amount=0.0):
        pass


class ForexHolding(BaseHolding):
    """This class handles currency exchanges."""

    @property
    def balance(self):
        """Return the value of this holding in your native currency."""
        return self.n_units / self.current_price

    def buy(self, n_units=0.0, amount=0.0):
        """
        Buy foreign currency.

        :param n_units: The amount of foreign currency (in that currency) to buy.
        :param amount: The amount of native currency to convert to foreign currency.
        :raise ValueError: Raised if both n_units and amount are 0.0 (default values), else n_units takes priority.
        :return:
        """
        assert isinstance(n_units, (int, float))
        assert isinstance(amount, (int, float))
        if n_units != 0.0:
            self.n_units += n_units
        elif amount != 0.0:
            self.n_units += (amount * self.current_price)
        else:
            raise ValueError('You must specify either the number of units (n_units) or the amount (amount) '
                             'that you wish to purchase.')

    def sell(self, n_units=0.0, amount=0.0):
        """
        Sell foreign currency.

        :param n_units: The amount of foreign currency you wish to convert back.
        :param amount: The amount of native you wish to buy back.
        :raise ValueError: Raised if both n_units and amount are 0.0 (default values), else n_units takes priority.
        :return:
        """
        assert isinstance(n_units, (int, float))
        assert isinstance(amount, (int, float))
        if n_units != 0.0:
            self.n_units -= n_units
        elif amount != 0.0:
            self.n_units -= (amount * self.current_price)
        else:
            raise ValueError('You must specify either the number of units (n_units) or the amount (amount) '
                             'that you wish to sell.')
