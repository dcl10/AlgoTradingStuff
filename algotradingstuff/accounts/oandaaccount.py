import requests
import os
import datetime as dt
from algotradingstuff.accounts.errors import AccountError


class OandaAccount:
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

    def update_account_state(self, last_transaction_id: str):
        """
        Update the information about the account's price dependent state since the most
        recent transaction.
        :param last_transaction_id: The ID of the most recent transaction
        :returns: bool
        :raises: AccountError
        """
        response = requests.get(f'{self.base_url}/accounts/{self.id}/changes',
                                headers={'Authorization': f'Bearer {self.api_key}',
                                         'Content-Type': 'application/json'},
                                params={'sinceTransactionID': last_transaction_id})
        code = response.status_code
        reason = response.reason
        state = response.json().get('state', {})
        response.close()
        if state != {}:
            self.__dict__.update(**state)
            return True
        else:
            raise AccountError(f'failed to update state of account with ID: {self.id}.' + os.linesep +
                               f'Reason {reason}' + os.linesep + f'Code {code}')

    def update_account_changes(self, last_transaction_id: str):
        """
        Update the account with changes to orders, trades, positions and balance since the most
        recent transaction.
        :param last_transaction_id: The ID of the most recent transaction
        :returns: bool
        :raises: AccountError
        """
        response = requests.get(f'{self.base_url}/accounts/{self.id}/changes',
                                headers={'Authorization': f'Bearer {self.api_key}',
                                         'Content-Type': 'application/json'},
                                params={'sinceTransactionID': last_transaction_id})
        code = response.status_code
        reason = response.reason
        changes = response.json().get('changes', {})
        response.close()
        if changes != {}:
            self.__dict__.update(**changes)
            return True
        else:
            raise AccountError(f'failed to update changes of account with ID: {self.id}.' + os.linesep +
                               f'Reason {reason}' + os.linesep + f'Code {code}')

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
        :returns: requests.PreparedRequest
        """
        req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/trades/{trade_specifier}/close',
                               headers={'Authorization': f'Bearer {self.api_key}',
                                        'Content-Type': 'application/json'},
                               method='PUT')
        return req.prepare()

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
        if start != '' and end != '':
            start = dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timestamp()
            end = dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S').timestamp()
            req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/instruments/{instrument}/candles',
                                   headers={'Authorization': f'Bearer {self.api_key}',
                                            'Accept-Datetime-Format': 'UNIX'},
                                   params={'granularity': granularity, 'price': price,
                                           'from': start, 'to': end},
                                   method='GET')
        elif start == '' and end != '':
            end = dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S').timestamp()
            req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/instruments/{instrument}/candles',
                                   headers={'Authorization': f'Bearer {self.api_key}',
                                            'Accept-Datetime-Format': 'UNIX'},
                                   params={'granularity': granularity, 'price': price,
                                           'to': end, 'count': count},
                                   method='GET')
        elif end == '' and start != '':
            start = dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timestamp()
            req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/instruments/{instrument}/candles',
                                   headers={'Authorization': f'Bearer {self.api_key}',
                                            'Accept-Datetime-Format': 'UNIX'},
                                   params={'granularity': granularity, 'price': price,
                                           'from': start, 'count': count},
                                   method='GET')
        else:
            req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/instruments/{instrument}/candles',
                                   headers={'Authorization': f'Bearer {self.api_key}',
                                            'Accept-Datetime-Format': 'UNIX'},
                                   params={'granularity': granularity, 'price': price,
                                           'count': count},
                                   method='GET')
        return req.prepare()

    def get_transactions(self, start: str = '', end: str = ''):
        """
        Make a request to get the transactions for the account. If `start` and `end` are blank,
        it will request all transactions since the account creation to the most recent transaction.
        :param start: a date string, in the format 'yyyy-mm-dd hh:mm:ss', for the start point of your search
        :param end: a date string, in the format 'yyyy-mm-dd hh:mm:ss', for the end point of your search
        :returns: requests.PreparedRequest
        """
        if start != '' and end != '':
            start = dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timestamp()
            end = dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S').timestamp()
            req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/transactions',
                                   headers={'Authorization': f'Bearer {self.api_key}',
                                            'Accept-Datetime-Format': 'UNIX'},
                                   params={'from': start, 'to': end},
                                   method='GET')
        elif start == '' and end != '':
            end = dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S').timestamp()
            req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/transactions',
                                   headers={'Authorization': f'Bearer {self.api_key}',
                                            'Accept-Datetime-Format': 'UNIX'},
                                   params={'to': end},
                                   method='GET')
        elif end == '' and start != '':
            start = dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timestamp()
            req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/transactions',
                                   headers={'Authorization': f'Bearer {self.api_key}',
                                            'Accept-Datetime-Format': 'UNIX'},
                                   params={'from': start},
                                   method='GET')
        else:
            req = requests.Request(url=f'{self.base_url}/accounts/{self.id}/transactions',
                                   headers={'Authorization': f'Bearer {self.api_key}',
                                            'Accept-Datetime-Format': 'UNIX'},
                                   method='GET')
        return req.prepare()


def get_accounts(api_key: str, base_url: str):
    """
    Retrieve a list of account dicts if the request is successful
    :param base_url: base URL for the OANDA API
    :param api_key: The API key for your OANDA account
    :raises: AccountError
    :returns: list[OandaAccount]
    """
    response = requests.get(f'{base_url}/accounts',
                            headers={'Authorization': f'Bearer {api_key}'})
    code = response.status_code
    reason = response.reason
    accounts = response.json().get('accounts', [])
    response.close()
    if accounts:
        return [OandaAccount(api_key, base_url, **account) for account in accounts]
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
    :returns: OandaAccount
    """
    response = requests.get(f'{base_url}/accounts/{account_id}',
                            headers={'Authorization': f'Bearer {api_key}'})
    code = response.status_code
    reason = response.reason
    account = response.json().get('account', {})
    response.close()
    if account != {}:
        return OandaAccount(api_key, base_url, **account)
    else:
        raise AccountError(f'failed to get account with ID: {account_id}.' + os.linesep +
                           f'Reason {reason}' + os.linesep + f'Code {code}')
