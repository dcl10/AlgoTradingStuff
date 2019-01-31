class Portfolio:

    def __init__(self, name, pot=0.0):
        self.name = name
        self.holdings = {}
        self.pot = pot

    def add_holdings(self, *args, **kwargs):
        if args:
            for arg in args:
                self.holdings.update({arg.name: arg})
        if kwargs:
            self.holdings.update(**kwargs)

    def remove_holding(self, *args):
        for arg in args:
            del self.holdings[arg]

    @property
    def current_value(self):
        return sum([h.balance for h in self.holdings])

    @property
    def returns(self):
        return self.current_value / self.pot

    def allocate(self, holding, amount):
        pass


class BaseHolding:

    def __init__(self, name, pot=0.0):
        self.name = name
        self.pot = pot
