import unittest
import os
import json
from docker.errors import APIError

from mock_docker import MockDocker


class TestMockClient(unittest.TestCase):

    def setUp(self):
        f = open(os.path.join(os.path.dirname(__file__), 'mockClient.json'), 'r')
        self.client_dict = json.load(f)
        self.mock_client = MockDocker(client_dict=self.client_dict)
        f.close()
        

    def test_DockerClient(self):
        """
        Test that DockerClient will successfuly "connect" to a node in the MockDocker instance
        """
        node_dict = self.client_dict['nodes'][0]
        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")
        
        self.assertEqual(client._active_server, node_dict)


class TestnodesClass(unittest.TestCase):
    """
    Tests get and list functions
    """
    def setUp(self):
        f = open(os.path.join(os.path.dirname(__file__), 'mockClient.json'), 'r')
        self.client_dict = json.load(f)
        self.mock_client = MockDocker(client_dict=self.client_dict)
        f.close()

    def test_get_non_existant_node(self):
        """
        Test that get() raises an API error when a node is not found
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is not None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes in a swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")

        with self.assertRaises(APIError):
            client.nodes.get(id_or_name="non_existant_node")

    def test_get_node_not_in_swarm(self):
        """
        Test that get raises an API error when the current client is not part of a swarm
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes not in swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")

        with self.assertRaises(APIError):
            client.nodes.get(id_or_name="non_existant_node")

    def test_get_existing_node(self):
        """
        Test that get returns a Node object
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is not None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes not in swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")
        
        self.assertIsInstance(client.nodes.get(node_dict['attrs']['ID']), MockDocker.Node)
        self.assertIsInstance(client.nodes.get(node_dict['attrs']['Spec']['Name']), MockDocker.Node)

    def test_list_node_not_in_swarm(self):
        """
        Tests that list() raises an APIError if client node is not part of a swarm
        """

        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes not in swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")

        with self.assertRaises(APIError):
            client.nodes.list()

    def test_list_nodes_in_swarm(self):
        """
        Test that list() returns a list of all nodes in the connected swarm
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is not None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes in swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")
        # Get all nodes in the swarm
        swarm_nodes = []
        for node in self.client_dict['nodes']:
            if node['swarm'] == node_dict['swarm']:
                swarm_nodes.append(node)

        self.assertEqual(len(client.nodes.list()), len(swarm_nodes))
     
    def test_list_nodes_in_swarm_with_filter_by_id(self):
        """
        Tests that list() returns a list of nodes with id filters
        """

        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is not None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes in swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")
        
        short_id = node_dict['attrs']['ID'][:3]
        filtered_node_list = []
        for node in self.client_dict['nodes']:
            if node['swarm'] == node_dict['swarm'] and short_id in node['attrs']['ID']:
                filtered_node_list.append(node)

        self.assertEqual(len(client.nodes.list(filters={'id': short_id})), len(filtered_node_list))

    def test_list_nodes_in_swarm_with_filter_by_name(self):
        """
        Tests that list() returns a list of nodes with name filters
        """

        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is not None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes in swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")
        
        name = node_dict['attrs']['Spec']['Name']
        filtered_node_list = []
        for node in self.client_dict['nodes']:
            if node['swarm'] == node_dict['swarm'] and name in node['attrs']['Spec']['Name']:
                filtered_node_list.append(node)

        self.assertEqual(len(client.nodes.list(filters={'name': name})), len(filtered_node_list))

    def test_list_nodes_in_swarm_with_filter_by_role(self):
        """
        Test List Nodes in Swarm filtered by role
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is not None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes in swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")
        
        role = node_dict['attrs']['Spec']['Role']
        filtered_node_list = []
        for node in self.client_dict['nodes']:
            if node['swarm'] == node_dict['swarm'] and role in node['attrs']['Spec']['Role']:
                filtered_node_list.append(node)

        self.assertEqual(len(client.nodes.list(filters={'role': role})), len(filtered_node_list))


class TestNodeClass(unittest.TestCase):
    """
    Tests for MockDocker.Node class
    """
    def setUp(self):
        f = open(os.path.join(os.path.dirname(__file__), 'mockClient.json'), 'r')
        self.client_dict = json.load(f)
        self.mock_client = MockDocker(client_dict=self.client_dict)
        f.close()

    def test_node_update(self):
        """
        Test the update function will update a node appropriatly
        """

        node_dict = None
        for node in self.client_dict['nodes']:
            # Find the first node that meets test requirements
            if node['swarm'] is not None and node['state'] == 'success':
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes in swarm found with success state")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")
        node = client.nodes.get(node_dict['attrs']['ID'])

        new_node_spec = {
            'Availability': 'pause',
            'Role': 'worker',
            'Name': 'asdfl;kjasrftg',
            'Labels': {}
        }
        node.update(new_node_spec)
        self.assertEqual(client._active_server['attrs']['Spec'], new_node_spec)

    def test_node_update_fail(self):
        """
        Test that Node.update() fails when passed a node in a fail state
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            # Find the first node that meets test requirements
            if node['swarm'] is not None and node['state'] == 'fail':
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes in swarm found with fail state")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")
        node = client.nodes.get(node_dict['attrs']['ID'])

        new_node_spec = {
            'Availability': 'pause',
            'Role': 'worker',
            'Name': 'asdfl;kjasrftg',
            'Labels': {}
        }
        with self.assertRaises(APIError):
            node.update(new_node_spec)

    def test_node_reload(self):
        """
        Test that reload will adjust the state and allow an update to pass
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            # Find the first node that meets test requirements
            if node['swarm'] is not None and node['state'] == 'fail':
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes in swarm found with fail state")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")
        node = client.nodes.get(node_dict['attrs']['ID'])

        new_node_spec = {
            'Availability': 'pause',
            'Role': 'worker',
            'Name': 'asdfl;kjasrftg',
            'Labels': {}
        }
        with self.assertRaises(APIError):
            node.update(new_node_spec)

        node.reload()
        node.update(new_node_spec)
        self.assertEqual(client._active_server['attrs']['Spec'], new_node_spec)
        self.assertEqual(client._active_server['state'], 'fail')


class TestSwarmClass(unittest.TestCase):
    """
    Tests to verify functionality of the MockDocker.Swarm class
    """
    def setUp(self):
        f = open(os.path.join(os.path.dirname(__file__), 'mockClient.json'), 'r')
        self.client_dict = json.load(f)
        self.mock_client = MockDocker(client_dict=self.client_dict)
        f.close()

    def test_swarm_init(self):
        """
        Test that when a connection is made swarm is generated and populated with expected data
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is not None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes in swarm found")
        swarm_dict = None
        for swarm in self.client_dict['swarms']:
            if swarm['id'] == node_dict['swarm']:
                swarm_dict = swarm
                break
        if not swarm_dict:
            raise Exception("No Swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")
        
        self.assertIsNotNone(client.swarm.attrs)
        self.assertEqual(client.swarm.attrs, swarm_dict['attrs'])

    def test_get_unlock_key(self):
        """
        Test that UnlockKey is returned in a dictionary
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is not None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes in swarm found")
        swarm_dict = None
        for swarm in self.client_dict['swarms']:
            if swarm['id'] == node_dict['swarm']:
                swarm_dict = swarm
                break
        if not swarm_dict:
            raise Exception("No Swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")
        
        self.assertEqual(client.swarm.get_unlock_key().get('UnlockKey'), swarm_dict.get('UnlockKey'))

    def test_join_fails_if_node_in_swarm(self):
        """
        Test that join will fill if the node is already a member of a swarm
        """

        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is not None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes in swarm found")
        
        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")

        with self.assertRaises(APIError):
            client.swarm.join(remote_addrs=[node_dict['attrs']['Status']['Addr']], join_token='asdfasfasf')

    def test_join_fails_with_no_join_token(self):
        """
        Test that Join will Fail if no join token is passed or incorrect join token is passed
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes not in swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")

        # Test with no join token passed
        with self.assertRaises(APIError):
            client.swarm.join(remote_addrs=[node_dict['attrs']['Status']['Addr']])

    def test_join_fails_with_wrong_token(self):
        """
        Test that Join will Fail if no join token is passed or incorrect join token is passed
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes not in swarm found")

        swarm_node = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is not None:
                swarm_node = node
                break
        if not swarm_node:
            raise Exception("No Nodes in swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")

        # Test with incorrect join token passed
        with self.assertRaises(APIError):
            client.swarm.join(remote_addrs=[swarm_node['attrs']['Status']['Addr']], join_token='[]/;.;l')

    def test_join_invalid_addrs(self):
        """
        Test that Join will Fail if no join token is passed or incorrect join token is passed
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes not in swarm found")


        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")

        # Test with incorrect join token passed
        with self.assertRaises(APIError):
            client.swarm.join(remote_addrs=['no_address_here'], join_token="fake_join_token")

    def test_join_swarm_with_worker_token(self):
        """
        Test that join will successfully join a swarm
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes not in swarm found")

        swarm_node = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is not None:
                swarm_node = node
                break
        if not swarm_node:
            raise Exception("No Nodes in swarm found")

        # Get the swarm token
        for swarm in self.client_dict['swarms']:
            if swarm['id'] == swarm_node['swarm']:
                swarm_token = swarm['attrs']['JoinTokens']['Worker']
                break
        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")

        self.assertTrue(client.swarm.join(remote_addrs=[swarm_node['attrs']['Status']['Addr']], join_token=swarm_token))
        self.assertEqual(client.nodes.get(node_dict['attrs']['ID']).attrs['Spec']['Role'], 'worker')
        self.assertEqual(client._active_server['swarm'], swarm['id'])

    def test_join_swarm_with_manager_token(self):
        """
        Test that join will successfully join a swarm
        """
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is None:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No Nodes not in swarm found")

        swarm_node = None
        for node in self.client_dict['nodes']:
            if node['swarm'] is not None:
                swarm_node = node
                break
        if not swarm_node:
            raise Exception("No Nodes in swarm found")

        # Get the swarm token
        for swarm in self.client_dict['swarms']:
            if swarm['id'] == swarm_node['swarm']:
                swarm_token = swarm['attrs']['JoinTokens']['Manager']
                break
        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")

        self.assertTrue(client.swarm.join(remote_addrs=[swarm_node['attrs']['Status']['Addr']], join_token=swarm_token))
        self.assertEqual(client.nodes.get(node_dict['attrs']['ID']).attrs['Spec']['Role'], 'manager')
        self.assertEqual(client._active_server['swarm'], swarm['id'])

    def test_reload_swarm(self):
        """
        Test that reload will change the swarm state from fail to reload
        """
        # Find a swarm set to fail
        fail_swarm = None
        for swarm in self.client_dict['swarms']:
            if swarm['state'] == 'fail':
                fail_swarm = swarm
                break
        if not fail_swarm:
            raise Exception("No swarm in fail state found")

        # Find a node in the swarm
        swarm_id = fail_swarm['id']
        for node in self.client_dict['nodes']:
            if node['swarm'] == swarm_id:
                node_dict = node
                break
        
        if not node_dict:
            raise Exception("No node in swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")

        self.assertTrue(client.swarm.reload())
        self.assertEqual(client.swarm._state, "reload")