from requests import Session


class OandaSession(Session):

    def send(self, request, **kwargs):
        res = super().send(request)
        res_json = res.json()
        if 'lastTransactionID' in res_json:
            last_transaction_id = res_json.pop('lastTransactionID')
        else:
            last_transaction_id = None
        return res_json, last_transaction_id
