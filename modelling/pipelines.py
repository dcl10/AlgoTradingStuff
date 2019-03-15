import numpy as np
import pandas as pd

from portfolio.portfolio import make_holding
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima_model import ARMA
from itertools import permutations


class Pipeline:

    def __init__(self, data, prices, target=None, threads=1):
        self.threads = threads
        self.data = data
        self.target = target
        self.prices = prices
        self._clf_report = None
        self._predictor = None
        self._labeler = None

    def _is_stationary(self):
        test: tuple = adfuller(self.data[self.prices])  # type annotation stops PyCharm yelling at me
        return test[1] < 0.05

    def _train_predictor(self):
        perms = list(permutations([0, 1, 2, 3, 4], 2))
        aics = []
        for i in perms:
            arima = ARMA(self.data, order=i).fit()
            aics.append(arima.aic)
        orders = perms[aics.index(min(aics))]
        self._predictor = ARMA(self.data, order=orders).fit()

    def _train_labeler(self):
        x = self.data.drop(self.target, axis=1)
        y = self.data[self.target]
        x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.7, random_state=42)
        self._labeler = LogisticRegression()
        self._labeler.fit(x_train, y_train)
        preds = self._labeler.predict(x_test)
        self._clf_report = classification_report(y_true=y_test, y_pred=preds)

    def feed(self, kind, name, data, price_col, n_units=0.0):
        holding = make_holding(kind, name, data, price_col, n_units)


if __name__ == '__main__':
    pipe = Pipeline(pd.DataFrame(), 'close', 'label')
    perms = permutations([0, 1, 2, 3, 4], 2)
    print(list(perms))
