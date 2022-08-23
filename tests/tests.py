import unittest
import os
import json
from docker.errors import APIError

from mock_client import MockClient


class TestMockClient(unittest.TestCase):

    def setUp(self):
        self.mock_client = MockClient()
        f = open(os.path.join(os.path.dirname(__file__), 'mockClient.json'))
        self.client_dict = json.load(f)
        

    def test_build_from_file(self):
        """
            Tests that load_from_file successfully creates populated MockClient object.
        """
        mock_client = MockClient()
        
        self.assertTrue(mock_client.build_from_file(os.path.join(os.path.dirname(__file__), 'mockClient.json')))
        mock_client.close()
