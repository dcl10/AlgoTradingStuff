from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima_model import ARMA
from itertools import combinations_with_replacement
from multiprocessing import Pool

import numpy as np
import pandas as pd


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
        test = adfuller(self.data[self.prices])
        return test[1] < 0.05

    def _train_predictor(self):
        perms = list(range(1, 6))
        aics = []
        for i in perms:
            arima = ARMA(self.data[self.prices], order=(0, i)).fit()
            aics.append(arima.aic)
        orders = (0, perms[aics.index(min(aics))])
        print(orders)
        # self._predictor = ARMA(self.data, order=orders).fit()

    # TODO: find another way to parallelise this function
    def _train_predictor_para(self):
        # Wrapper for `ARMA.fit` to make it compatible with `Pool.map`
        def _fit(mod):
            return mod.fit()
        perms = list(permutations([0, 1, 2, 3, 4], 2))
        pool = Pool(processes=self.threads)
        mods = [ARMA(self.data[self.prices], order=i) for i in perms]
        aics = [fit.aic for fit in pool.map(_fit, mods)]
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

    def _train_labeler_para(self):
        x = self.data.drop(self.target, axis=1)
        y = self.data[self.target]
        x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.7, random_state=42)
        self._labeler = LogisticRegression(n_jobs=self.threads)
        self._labeler.fit(x_train, y_train)
        preds = self._labeler.predict(x_test)
        self._clf_report = classification_report(y_true=y_test, y_pred=preds)

    def train(self):
        if self.threads > 1:
            if self._is_stationary():
                self._train_predictor_para()
                # self._train_labeler_para()
        else:
            if self._is_stationary():
                self._train_predictor()
                # self._train_labeler()


if __name__ == '__main__':
    data = pd.read_csv('aapl_test.csv', index_col='Date', parse_dates=True)
    data.drop('Dividend', axis=1, inplace=True)
    data = data.pct_change().dropna()
    data = data.resample('D').sum()
    print(adfuller(data['Adj_Close'])[1] <= 0.05)
    pipe = Pipeline(data=data, prices='Adj_Close')
    pipe.train()
