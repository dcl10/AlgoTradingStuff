class Portfolio:

    def __init__(self, name, pot=0.0):
        self.name = name
        self.holdings = {}
        self.pot = pot

    @property
    def current_value(self):
        return sum([h.balance for h in self.holdings])

    @property
    def returns(self):
        return self.current_value / self.pot

    def add_holdings(self, *args, **kwargs):
        if args:
            for arg in args:
                self.holdings.update({arg.name: arg})
        if kwargs:
            self.holdings.update(**kwargs)

    def remove_holdings(self, *args):
        for arg in args:
            del self.holdings[arg]

    def allocate(self, holding, amount):
        self.holdings[holding].pot += amount


class BaseHolding:

    def __init__(self, name, n_units=0):
        self.name = name
        self.current_price = self.get_current_price()
        self.n_units = n_units

    @property
    def balance(self):
        return self.current_price * self.n_units

    def get_current_price(self):
        return 0.0  # TODO replace with call to quandl API

    def buy(self, n_units=None, amount=None):
        if n_units is not None:
            self.n_units += n_units
        elif amount is not None:
            self.n_units += amount / self.current_price
        else:
            raise TypeError('You must specify either the number of units (n_units) or the amount (amount) '
                            'that you wish to purchase.')

    def sell(self, n_units=None, amount=None):
        if n_units is not None:
            self.n_units -= n_units
        elif amount is not None:
            self.n_units -= amount / self.current_price
        else:
            raise TypeError('You must specify either the number of units (n_units) or the amount (amount) '
                            'that you wish to purchase.')

    def update(self):
        pass
