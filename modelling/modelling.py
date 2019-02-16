import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import quandl

import abc

from statsmodels.tsa.stattools import acf, adfuller, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_process import ArmaProcess
from statsmodels.tsa.arima_model import ARMA
from itertools import permutations


def label_data(data, label, decision_func, data_cols=None):
    if data_cols is None:
        data[label] = data.apply(decision_func)
    else:
        data[label] = data[data_cols].apply(decision_func)
    return data


def is_white_noise(data):
    result: tuple = adfuller(data)  # the type hint after `result` stops Pycharm telling me `result` is a float
    return result[1] >= 0.05


def get_sig_lags(data):
    result, confint = pacf(data, nlags=20, alpha=0.05)
    result = np.where(np.isnan(result), 0, result)
    confint = np.where(np.isnan(confint), 0, confint)
    sig = np.logical_or(result < confint[:, 0], result > confint[:, 1])
    sig_lags = [i for i in range(1, len(sig)) if sig[i]]
    return list(permutations(sig_lags, 2))


if __name__ == '__main__':
    arp = ArmaProcess(ar=[1, -.9, -0.5], ma=[1], nobs=1000)
    d = arp.generate_sample(100)
    print(is_white_noise(d))
    print(get_sig_lags(d))
