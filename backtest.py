import abc

from pipelines import Pipeline


class BaseBackTester(abc.ABC):

    @abc.abstractmethod
    def run(self):
        pass


class HoldingBackTester(BaseBackTester):

    def __init__(self, holding, initial, data, target='sell', threads=1):
        self.holding = holding
        self.initial = initial
        self.data = data
        self.target = target
        self.threads = threads

    def run(self):
        pipeline = Pipeline(self.holding.data,
                            self.holding.data[self.holding.price_col],
                            target=self.target,
                            threads=self.threads)
        pipeline.train()


class PortfolioBackTester(BaseBackTester):

    def run(self):
        pass

    def _run_para(self):
        pass

    def _run(self):
        pass
