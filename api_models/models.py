import requests
from api_models.errors import AccountError


class Account:

    def __init__(self, api_key, **kwargse):
        self.api_key = api_key
        self.__dict__.update(kwargse)

    def create_order(self, units, ):

        pass

    def cancel_order(self):
        pass


def get_accounts(api_key: str):
    """
    Retrieve a list of account dicts if the request is successful, else return None
    :param api_key: The API key for your OANDA account
    :return: Return list of accounts if request of successful, else None
    """
    response = requests.get('https://api-fxpractice.oanda.com/v3/accounts',
                            headers={'Authorization': f'Bearer {api_key}'})
    code = response.status_code
    reason = response.reason
    if code == 200:
        accounts = response.json().get('accounts')
        response.close()
        return accounts
    else:
        response.close()
        raise AccountError(f'AccountError: no accounts found. Reason: {reason}')


def get_account(account_id: str, api_key: str):
    """
    Return the parameters for an individual account
    :param account_id: The id for the account to be retrieved
    :param api_key: the API for your OANDA account
    :return:
    """
    response = requests.get(f'https://api-fxpractice.oanda.com/v3/accounts/{account_id}',
                            headers={'Authorization': f'Bearer {api_key}'})
    code = response.status_code
    reason = response.reason
    if code == 200:
        account = response.json().get('account')
        response.close()
        return account
    else:
        response.close()
        raise AccountError(f'AccountError: failed to get account with ID: {account_id}, '
                           f'Reason {reason}')
