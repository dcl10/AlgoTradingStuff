import requests
import os
import json
import datetime as dt
from api_models.errors import AccountError


class Account:
    """
    This class hold information about an OANDA account
    """

    def __init__(self, api_key, base_url, **kwargs):
        """

        :param api_key:
        :param base_url:
        :param account_id:
        :param kwargs:
        """
        self.api_key = api_key
        self.base_url = base_url
        self.__dict__.update(kwargs)

    # def __repr__(self):
    #     return f'Account(api_key: <secret>, base_url: {self.base_url}, account_id: {self.account_id}'
    #
    # def __str__(self):
    #     return self.account_id

    def create_order(self, data: dict):
        """
        This method creates a request for an order of the specified type and amount of units
        :param data: a dict with the parameters of the order to be created
        :returns: requests.PreparedRequest
        """
        req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/orders',
                               headers={'Authorization': f'Bearer {self.api_key}',
                                        'Content-Type': 'application/json'},
                               method='POST',
                               json=data)
        return req.prepare()

    def get_orders(self):
        """
        This method creates a request to get all orders for the account
        :returns: requests.PreparedRequest
        """
        req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/orders',
                               headers={'Authorization': f'Bearer {self.api_key}',
                                        'Content-Type': 'application/json'},
                               method='GET')
        return req.prepare()

    def cancel_order(self, order_id: str):
        """
        This method makes a request to cancel the specified order
        :param order_id: the identifier of the order to be cancelled
        :returns: requests.PreparedRequest
        """
        req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/orders/{order_id}/cancel',
                               headers={'Authorization': f'Bearer {self.api_key}',
                                        'Content-Type': 'application/json'},
                               method='PUT')
        return req.prepare()

    def get_open_positions(self):
        """
        This method makes a request to get all the open positions for the account
        :returns: requests.PreparedRequest
        """
        req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/openPositions',
                               headers={'Authorization': f'Bearer {self.api_key}',
                                        'Content-Type': 'application/json'},
                               method='GET')
        return req.prepare()

    def close_position(self, instrument: str, long: bool):
        """
        This method makes a request to close the position for the provided instrument
        :param instrument: The instrument to close position
        :param long: True to close longPosition, False to close shortPosition
        :returns: requests.PreparedRequest
        """
        if long:
            data = {'longUnits': 'ALL'}
        else:
            data = {'shortUnits': 'ALL'}
        req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/positions/{instrument}/close',
                               headers={'Authorization': f'Bearer {self.api_key}',
                                        'Content-Type': 'application/json'},
                               method='PUT',
                               json=data)
        return req.prepare()

    def get_open_trades(self):
        """
        This method makes a request to get all the open trades for the account
        :returns: requests.PreparedRequest
        """
        req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/openTrades',
                               headers={'Authorization': f'Bearer {self.api_key}',
                                        'Content-Type': 'application/json'},
                               method='GET')
        return req.prepare()

    def close_trade(self, trade_specifier: str):
        """
        This method closes a trade with the provided trade specifier
        :param trade_specifier:
        :return:
        """
        pass

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
        pass


def get_accounts(api_key: str, base_url: str):
    """
    Retrieve a list of account dicts if the request is successful
    :param base_url: base URL for the OANDA API
    :param api_key: The API key for your OANDA account
    :raises: AccountError
    :returns: list[Account]
    """
    response = requests.get(f'{base_url}/accounts',
                            headers={'Authorization': f'Bearer {api_key}'})
    code = response.status_code
    reason = response.reason
    accounts = response.json().get('accounts', [])
    response.close()
    if accounts:
        return [Account(api_key, base_url, **account) for account in accounts]
    else:
        raise AccountError(f'no accounts found.' + os.linesep + f'Reason {reason}' + os.linesep +
                           f'Code {code}')


def get_account(account_id: str, api_key: str, base_url: str):
    """
    Return the parameters for an individual primary_account
    :param account_id: The id for the primary_account to be retrieved
    :param api_key: the API for your OANDA primary_account
    :param base_url: base URL for the OANDA API
    :raises: AccountError
    :returns: Account
    """
    response = requests.get(f'{base_url}/accounts/{account_id}/summary',
                            headers={'Authorization': f'Bearer {api_key}'})
    code = response.status_code
    reason = response.reason
    account = response.json().get('account', {})
    response.close()
    if account != {}:
        return Account(api_key, base_url, **account)
    else:
        raise AccountError(f'failed to get account with ID: {account_id}.' + os.linesep +
                           f'Reason {reason}' + os.linesep + f'Code {code}')
