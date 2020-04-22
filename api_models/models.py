import requests
import os
import json
import datetime as dt
import time
from api_models.errors import AccountError


class Account:
    """
    This class hold information about an OANDA account
    """

    def __init__(self, api_key: str, base_url: str, account_id: str, **kwargs):
        """

        :param api_key:
        :param base_url:
        :param account_id:
        :param kwargs:
        """
        self.api_key = api_key
        self.base_url = base_url
        self.account_id = account_id
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f'Account(api_key: <secret>, base_url: {self.base_url}, account_id: {self.account_id}'

    def __str__(self):
        return self.account_id

    def create_order(self, data: dict):
        """
        This method creates an order of the specified type and amount of units
        :param data: a dict with the parameters of the order to be created
        :return: either a dict with information about the new order, or and empty dict if the order failed
        """
        req = requests.post(f'{self.base_url}/accounts/{self.account_id}/orders',
                            json=data,
                            headers={'Authorization': f'Bearer {self.api_key}',
                                     'Accept-Datetime-Format': 'UNIX'})
        response = req.json()
        req.close()
        new_details = get_account(self.account_id, self.api_key, base_url=self.base_url)
        self.__dict__.update(new_details)
        order = response.get('orderCreateTransaction', {})
        return order

    def cancel_order(self, order_id: str):
        """
        This method cancels the specified order
        :param order_id: the identifier of the order to be cancelled
        :return: a dict of the details of the cancellation, or a empty dict if the cancellation failed
        """
        response = requests.put(f'{self.base_url}/accounts/{self.account_id}/orders/{order_id}/cancel',
                                headers={'Authorization': f'Bearer {self.api_key}',
                                         'Accept-Datetime-Format': 'UNIX'})
        result = response.json()
        response.close()
        new_details = get_account(self.account_id, self.api_key, base_url=self.base_url)
        self.__dict__.update(new_details)
        cancel = result.get('orderCancelTransaction', {})
        return cancel

    def get_open_positions(self):
        """
        This method gets all the open positions for the account
        :return: a list of open positions, or an empty list if no positions
        """
        response = requests.get(f'{self.base_url}/accounts/{self.account_id}/openPositions',
                                headers={'Authorization': f'Bearer {self.api_key}'})
        code = response.status_code
        reason = response.reason
        result = response.json()
        response.close()
        if code == 200:
            return result.get('positions', [])
        else:
            raise AccountError(f'Could not find any open positions for {self.account_id}. Reason {reason}')

    def close_position(self, instrument: str, long: bool):
        """
        This method closes the position for the provided instrument
        :param instrument:
        :param long:
        :return:
        """
        if long:
            units_to_close = {'longUnits': "ALL"}
        else:
            units_to_close = {'shortUnits': "ALL"}
        response = requests.put(f'{self.base_url}/accounts/{self.account_id}/positions/{instrument}/close',
                                headers={'Authorization': f'Bearer {self.api_key}',
                                         'Content-Type': 'application/json'},
                                data=json.dumps(units_to_close))
        result = response.json()
        response.close()
        new_details = get_account(self.account_id, self.api_key, base_url=self.base_url)
        self.__dict__.update(new_details)
        return result

    def get_open_trades(self):
        """
        This method gets all the open trades for the account
        :return:
        """
        response = requests.get(f'{self.base_url}/accounts/{self.account_id}/openTrades',
                                headers={'Authorization': f'Bearer {self.api_key}',
                                         'Accept-Datetime-Format': 'UNIX'})
        result = response.json()
        response.close()
        return result.get('trades', [])

    def close_trade(self, trade_specifier: str):
        """
        This method closes a trade with the provided trade specifier
        :param trade_specifier:
        :return:
        """
        response = requests.put(f'{self.base_url}/accounts/{self.account_id}/trades/{trade_specifier}/close',
                                headers={'Authorization': f'Bearer {self.api_key}',
                                         'Content-Type': 'application/json',
                                         'Accept-Datetime-Format': 'UNIX'},
                                data=json.dumps({'units': "ALL"}))
        result = response.json()
        response.close()
        new_details = get_account(self.account_id, self.api_key, base_url=self.base_url)
        self.__dict__.update(new_details)
        return result.get('orderCreateTransaction', {})

    def get_candles(self, instrument: str, start: str = '', end: str = '', price: str = 'M',
                    granularity: str = 'M1', count: int = 500):
        """
        Get the candle data for a given instrument
        :param instrument: the instrument you want the candles for
        :param start: a date string, in the format 'yyyy-mm-dd hh:mm:ss', for the start point of your data range
        :param end: a date string, in the format 'yyyy-mm-dd hh:mm:ss', for the end point of your data range
        :param price: the price point of the candles. 'M' midpoint candles, 'B' bid candles, 'A' ask candles
        :param granularity: interval of the candles, see http://developer.oanda.com/rest-live-v20/instrument-df/#CandlestickGranularity
        :param count: how many rows of data to return
        :return:
        """
        # start = dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timestamp()
        # end = dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S').timestamp()
        # assert start < end, '`start` cannot be greater than or equal to `end`'
        if start != '' and end != '':
            start = dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timestamp()
            end = dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S').timestamp()
            response = requests.get(f'{self.base_url}/accounts/{self.account_id}/instruments/{instrument}/candles',
                                    headers={'Authorization': f'Bearer {self.api_key}',
                                             'Accept-Datetime-Format': 'UNIX'},
                                    params={'granularity': granularity, 'price': price,
                                            'from': start, 'to': end})
        elif start == '' and end != '':
            end = dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S').timestamp()
            response = requests.get(f'{self.base_url}/accounts/{self.account_id}/instruments/{instrument}/candles',
                                    headers={'Authorization': f'Bearer {self.api_key}',
                                             'Accept-Datetime-Format': 'UNIX'},
                                    params={'granularity': granularity, 'price': price,
                                            'to': end, 'count': count})
        elif end == '' and start != '':
            start = dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timestamp()
            response = requests.get(f'{self.base_url}/accounts/{self.account_id}/instruments/{instrument}/candles',
                                    headers={'Authorization': f'Bearer {self.api_key}',
                                             'Accept-Datetime-Format': 'UNIX'},
                                    params={'granularity': granularity, 'price': price,
                                            'from': start, 'count': count})
        else:
            response = requests.get(f'{self.base_url}/accounts/{self.account_id}/instruments/{instrument}/candles',
                                    headers={'Authorization': f'Bearer {self.api_key}',
                                             'Accept-Datetime-Format': 'UNIX'},
                                    params={'granularity': granularity, 'price': price,
                                            'count': count})
        result = response.json()
        response.close()
        return result.get('candles', [])


def get_accounts(api_key: str, base_url='https://api-fxpractice.oanda.com/v3'):
    """
    Retrieve a list of account dicts if the request is successful
    :param base_url: base URL for the OANDA API
    :param api_key: The API key for your OANDA account
    :raises: AccountError
    :return: Return list of accounts if request of successful, else None
    """
    response = requests.get(f'{base_url}/accounts',
                            headers={'Authorization': f'Bearer {api_key}'})
    code = response.status_code
    reason = response.reason
    accounts = response.json().get('accounts', [])
    response.close()
    if len(accounts) > 0:
        return accounts
    else:
        raise AccountError(f'no accounts found.' + os.linesep + f'Reason {reason}' + os.linesep +
                           f'Code {code}')


def get_account(account_id: str, api_key: str, base_url='https://api-fxpractice.oanda.com/v3'):
    """
    Return the parameters for an individual account
    :param base_url: base URL for the OANDA API
    :param account_id: The id for the account to be retrieved
    :param api_key: the API for your OANDA account
    :raises: AccountError
    :return:
    """
    response = requests.get(f'{base_url}/accounts/{account_id}/summary',
                            headers={'Authorization': f'Bearer {api_key}'})
    code = response.status_code
    reason = response.reason
    account = response.json().get('account', {})
    response.close()
    if account != {}:
        return account
    else:
        raise AccountError(f'failed to get account with ID: {account_id}.' + os.linesep +
                           f'Reason {reason}' + os.linesep + f'Code {code}')
