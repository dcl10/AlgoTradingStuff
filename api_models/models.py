import requests
import os
from api_models.errors import AccountError


class Account:
    """
    This class hold information about an OANDA account
    """

    def __init__(self, api_key, base_url, account_id, **kwargse):
        self.api_key = api_key
        self.base_url = base_url
        self.account_id = account_id
        self.__dict__.update(kwargse)

    def create_order(self, data):
        """
        This method creates an order of the specified type and amount of units
        :return:
        """
        req = requests.post(f'{self.base_url}/accounts/{self.account_id}/orders',
                            json=data,
                            headers={'Authorization': f'Bearer {self.api_key}'})
        code = req.status_code
        reason = req.reason
        response = req.json()
        req.close()
        if code == 201:
            new_details = get_account(self.account_id, self.api_key, base_url=self.base_url)
            self.__dict__.update(new_details)
            order = response.get('orderCreateTransaction')
            return order
        else:
            raise AccountError(f'unable to create the specified order. Reason {reason}')

    def cancel_order(self):
        """
        This method cancels the specified order
        :return:
        """
        pass


def get_accounts(api_key: str, base_url='https://api-fxpractice.oanda.com/v3'):
    """
    Retrieve a list of account dicts if the request is successful, else return None
    :param base_url: base URL for the OANDA API
    :param api_key: The API key for your OANDA account
    :raises: AccountError
    :return: Return list of accounts if request of successful, else None
    """
    response = requests.get(f'{base_url}/v3/accounts',
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
    response = requests.get(f'{base_url}/accounts/{account_id}',
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
