import os
import unittest
import requests

from algotradingstuff.sessions import OandaSession


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.api_key = os.getenv('API_KEY')
        self.account_id = os.getenv('ACCOUNT_ID')
        self.base_url = os.getenv('BASE_URL')
        self.request = requests.Request(url=f'{self.base_url}/accounts/{self.account_id}/summary',
                                        headers={'Authorization': f'Bearer {self.api_key}',
                                                 'Content-Type': 'application/json'},
                                        method='GET'
                                        ).prepare()
        self.no_lti_request = requests.Request(url=f'{self.base_url}/accounts',
                                               headers={'Authorization': f'Bearer {self.api_key}',
                                                        'Content-Type': 'application/json'},
                                               method='GET'
                                               ).prepare()
        self.session = OandaSession()

    def tearDown(self) -> None:
        self.session.close()

    def test_send(self):
        content, lti = self.session.send(self.request)
        self.assertIsInstance(lti, str)
        self.assertIsInstance(content, dict)
        no_lti_content, no_lti = self.session.send(self.no_lti_request)
        self.assertIsInstance(no_lti_content, dict)
        self.assertIsNone(no_lti)


if __name__ == '__main__':
    unittest.main()
