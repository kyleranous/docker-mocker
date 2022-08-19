import unittest
import os
import json
from docker.errors import APIError

from ..mock_client import MockClient


class TestMockClient(unittest.TestCase):

    def test_load_from_file(self):
        """
            Tests that load_from_file 
        """
        mock_client = MockClient()
        cwd = os.getcwd()
        
        self.assertTrue(mock_client.load_from_file(os.path.join(cwd, 'utils', 'docker_mocker', 'tests', 'mockClient.json')))


class TestMockNodes(unittest.TestCase):

    
    def setUp(self):
        self.cwd = os.getcwd()
        self.client = MockClient()
        self.client.load_from_file(os.path.join(self.cwd, 'utils', 'docker_mocker', 'tests', 'mockClient.json'))
        f = open(os.path.join(self.cwd, 'utils', 'docker_mocker', 'tests', 'mockClient.json'))
        self.client_dict = json.load(f)

    def tearDown(self):
        del self.client
        del self.client_dict

    def test_get_node_by_id(self):
        
        self.assertEqual(self.client.nodes.get('man_fail_node').attrs['Spec']['Name'], 'ManNode1')
    
    def test_get_node_by_name(self):

        self.assertEqual(self.client.nodes.get('ManNode1').id, 'man_fail_node')

    def test_get_node_not_found(self):

        with self.assertRaises(APIError):
            self.client.nodes.get('no_node')

    def test_list_nodes(self):

        nodes = self.client.nodes.list()
        self.assertEquals(len(nodes), len(self.client_dict['nodes']))

    def test_list_nodes_filtered_by_role(self):
        
        worker_nodes = self.client.nodes.list(filters={'role': 'worker'})
        man_nodes = self.client.nodes.list(filters={'role': 'manager'})

        json_workers = []
        json_man = []
        for node in self.client_dict['nodes']:
            if node['Spec']['Role'] == 'worker':
                json_workers.append(node)
            elif node['Spec']['Role'] == 'manager':
                json_man.append(node)

        self.assertEquals(len(worker_nodes), len(json_workers))
        self.assertEquals(len(man_nodes), len(json_man))

    def test_list_nodes_filterd_by_name(self):
        work_names = 'work'
        man_names = 'man'
        worker_nodes = self.client.nodes.list(filters={'name': work_names})
        man_nodes = self.client.nodes.list(filters={'name': man_names})
        
        json_work_names = []
        json_man_names = []
        for node in self.client_dict['nodes']:
            if work_names.lower() in node['Spec']['Name'].lower():
                json_work_names.append(node)
            if man_names.lower() in node['Spec']['Name'].lower():
                json_man_names.append(node)

        self.assertEquals(len(worker_nodes), len(json_work_names))
        self.assertEquals(len(man_nodes), len(json_man_names))

    def test_list_nodes_filterd_by_name(self):
        work_id = "work"
        man_id = "man"
        worker_nodes = self.client.nodes.list(filters={'id': work_id})
        man_nodes = self.client.nodes.list(filters={'id': man_id})

        json_work_ids = []
        json_man_ids = []
        for node in self.client_dict['nodes']:
            if work_id.lower() in node['ID'].lower():
                json_work_ids.append(node)
            if man_id.lower() in node['ID'].lower():
                json_man_ids.append(node)

        self.assertEquals(len(worker_nodes), len(json_work_ids))
        self.assertEquals(len(man_nodes), len(json_man_ids))
