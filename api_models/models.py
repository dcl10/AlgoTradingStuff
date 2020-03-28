import requests
import os
import json
import datetime as dt
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
        :param data:
        :return:
        """
        req = requests.post(f'{self.base_url}/accounts/{self.account_id}/orders',
                            json=data,
                            headers={'Authorization': f'Bearer {self.api_key}',
                                     'Accept-Datetime-Format': 'UNIX'})
        code = req.status_code
        reason = req.reason
        response = req.json()
        req.close()
        if code == 201:
            new_details = get_account(self.account_id, self.api_key, base_url=self.base_url)
            self.__dict__.update(new_details)
            order = response.get('orderCreateTransaction', {})
            return order
        else:
            raise AccountError(f'unable to create the specified order. Reason {reason}')

    def cancel_order(self, order_id: str):
        """
        This method cancels the specified order
        :param order_id:
        :return:
        """
        response = requests.put(f'{self.base_url}/accounts/{self.account_id}/orders/{order_id}/cancel',
                                headers={'Authorization': f'Bearer {self.api_key}',
                                         'Accept-Datetime-Format': 'UNIX'})
        code = response.status_code
        reason = response.reason
        result = response.json()
        response.close()
        if code == 200:
            new_details = get_account(self.account_id, self.api_key, base_url=self.base_url)
            self.__dict__.update(new_details)
            cancel = result.get('orderCancelTransaction', {})
            return cancel
        else:
            raise AccountError(f'unable to cancel order {order_id}. Reason {reason}')

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

    def close_position(self, instrument: str):
        """
        This method closes the position for the provided instrument
        :param instrument:
        :return:
        """
        response = requests.put(f'{self.base_url}/accounts/{self.account_id}/positions/{instrument}/close',
                                headers={'Authorization': f'Bearer {self.api_key}',
                                         'Content-Type': 'application/json'},
                                data=json.dumps({'longUnits': "ALL"}))
        code = response.status_code
        reason = response.reason
        result = response.json()
        response.close()
        if code == 200:
            new_details = get_account(self.account_id, self.api_key, base_url=self.base_url)
            self.__dict__.update(new_details)
            return result
        else:
            raise AccountError(f'unable to close position for {instrument}. Reason {reason}')

    def get_open_trades(self):
        """
        This method gets all the open trades for the account
        :return:
        """
        response = requests.get(f'{self.base_url}/accounts/{self.account_id}/openTrades',
                                headers={'Authorization': f'Bearer {self.api_key}',
                                         'Accept-Datetime-Format': 'UNIX'})
        code = response.status_code
        reason = response.reason
        result = response.json()
        response.close()
        if code == 200:
            return result.get('trades', [])
        else:
            raise AccountError(f'Could not find any open positions for {self.account_id}. Reason {reason}')

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
        code = response.status_code
        reason = response.reason
        result = response.json()
        response.close()
        if code == 200:
            new_details = get_account(self.account_id, self.api_key, base_url=self.base_url)
            self.__dict__.update(new_details)
            return result.get('orderCreateTransaction', {})
        else:
            raise AccountError(f'unable to close trade for {trade_specifier}. Reason {reason}')

    def get_candles(self, instrument, since, to, price='M', granularity='S5', count=500):
        """
        TODO: turns out the code on github wasn't using the `since` and `to` params.
        TODO: currently getting "Bad Request" with datetime objects. Find out why and fix
        :param instrument:
        :param since:
        :param to:
        :param price:
        :param granularity:
        :param count:
        :return:
        """
        assert since < to, '`since` cannot be greater than or equal to `to`'
        response = requests.get(f'{self.base_url}/accounts/{self.account_id}/instruments/{instrument}/candles',
                                headers={'Authorization': f'Bearer {self.api_key}',
                                         'Accept-Datetime-Format': 'UNIX'},
                                params={'granularity': granularity, 'price': price, 'from': since, 'to': str(to)})
        code = response.status_code
        reason = response.reason
        result = response.json()
        response.close()
        if code == 200:
            return result.get('candles')
        else:
            raise AccountError(f'unable to retrieve data with the specified parameters. Reason {reason}')


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
