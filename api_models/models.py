import requests


class Account:

    def __init__(self, api_key, **kwargse):
        self.api_key = api_key
        self.__dict__.update(kwargse)

    def create_order(self, units, ):

        pass

    def cancel_order(self):
        pass


def get_accounts(api_key):
    response = requests.get(f'https://api-fxpractice.oanda.com/v3/accounts/',
                            headers={'Authorization': f'Bearer {api_key}'})
    pass


def get_account(account_id: str, api_key: str):
    response = requests.get(f'https://api-fxpractice.oanda.com/v3/accounts/{account_id}')
    pass
