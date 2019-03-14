from portfolio.portfolio import make_holding


class Pipeline:

    def __init__(self, threads=1):
        self.threads = threads
        self.holding = None

    def _is_stationary(self):
        pass

    def _get_sig_lags(self):
        pass

    def _label_data(self, decision_func):
        pass

    def feed(self, kind, name, data, n_units=0.0, current_price=0.0):
        self.holding = make_holding(kind, name, data, n_units, current_price)


if __name__ == '__main__':
    pipe = Pipeline()
