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

    def __init__(self, name, n_units=0.0, current_price=0.0):
        self.name = name
        self.current_price = current_price
        self.n_units = n_units

    @property
    def balance(self):
        return self.current_price * self.n_units

    def buy(self, n_units=0.0, amount=0.0):
        assert isinstance(n_units, (float, int)), 'n_units must be a float or int'
        assert isinstance(amount, (float, int)), 'amount must be a float or int'
        if n_units != 0.0:
            self.n_units += n_units
        elif amount != 0.0:
            self.n_units += (amount / self.current_price)
        else:
            raise TypeError('You must specify either the number of units (n_units) or the amount (amount) '
                            'that you wish to purchase.')

    def sell(self, n_units=0.0, amount=0.0):
        assert isinstance(n_units, (float, int)), 'n_units must be a float or int'
        assert isinstance(amount, (float, int)), 'amount must be a float or int'
        if n_units != 0.0:
            self.n_units -= n_units
        elif amount != 0.0:
            self.n_units -= amount / self.current_price
        else:
            raise TypeError('You must specify either the number of units (n_units) or the amount (amount) '
                            'that you wish to purchase.')
