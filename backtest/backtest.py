class BackTester:
    """
    This class takes a set of buy/sell instructions and tests if they would make a profit in a given time range.
    """

    def __init__(self, balance: float, start: str, end: str, instructions: list, margin: float = 1.0):
        """

        :param balance:
        :param start:
        :param end:
        :param instructions:
        :param margin:
        """
        self.balance = balance
        self.start = start
        self.end = end
        self.instructions = instructions
        self.margin = margin
        self.result = balance

    def _sell(self):
        """
        Sell units
        :return:
        """
        self.result += (self.margin * self.result)

    def _buy(self):
        """
        Buy units
        :return:
        """
        self.result -= (self.margin * self.result)

    def run(self):
        """
        Runs the instructions given and determines total profit
        :return:
        """
        for ins in self.instructions:
            if ins:
                self._buy()
            else:
                self._sell()
