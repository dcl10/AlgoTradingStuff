class BackTester:
    """
    This class takes a set of buy/sell instructions and tests if they would make a profit in a given time range.
    """

    def __init__(self, balance: float, instructions: list, prices: list, margin: float = 1.0):
        """

        :param balance: The starting amount for the back-test
        :param instructions: A list of either booleans or ints in {0,1} where True/1 means buy and False/0 means sell
        :param prices: A list of prices at which to buy or units
        :param margin: The proportion of your balance you are willing to use in the transaction
        """
        self.balance = balance
        self.instructions = instructions
        self.margin = margin
        self.prices = prices
        self.result = balance

    def _sell(self, price: float):
        """
        Sell units
        :param price: the price at which to sell
        :return:
        """
        self.result += (self.margin * self.result) * price

    def _buy(self, price: float):
        """
        Buy units
        :param: the price at to buy
        :return:
        """
        self.result -= (self.margin * self.result) * price

    def run(self):
        """
        Runs the instructions given and determines total profit
        :return:
        """
        for ins, pri in zip(self.instructions, self.prices):
            if ins:
                self._buy(pri)
            else:
                self._sell(pri)
            print(f'{self.result:n}')