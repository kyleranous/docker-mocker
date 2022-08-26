import unittest
import os
import json
import copy

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
        self.mock_client = MockDocker(client_dict=dict(self.client_dict))
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

    def test_update_on_fail_swarm(self):
        """
        Test that Swarm.update() will raise API Error on a swarm set to fail
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

        with self.assertRaises(APIError):
            client.swarm.update()

    def test_update_swarm_without_token_rotation(self):
        """
        Test that Swarm.update() will update the appropriate fields in _attrs
        """
        update_dict = {
            "default_addr_pool": ['1.1.1.1', '1.1.1.2'],
            "subnet_size": 18,
            "data_path_addr": 1000,
            "task_history_retention_limit": 420,
            "snapshot_interval": 69,
            "keep_old_snapshots": 3,
            "log_entries_for_slow_followers": 1,
            "heartbeat_tick": 23,
            "election_tick": 22,
            "dispatcher_heartbeat_period": 50,
            "node_cert_expiry": 77777,
            "external_ca": {},
            "name": "this_has_been_updated",
            "labels": {
                "test_label": "Test Label"
            },
            "signing_ca_cert": "abc123",
            "signing_ca_key": "123abc",
            "ca_force_rotate": 123,
            "autolock_managers": False,
            "log_driver": {
                "test": "test"
            },
            "rotate_worker_token": False,
            "rotate_manager_token": False,
            "rotate_manager_unlock_key": False,
        }

        # Find a swarm that is in a success state
        success_swarm = None
        for swarm in self.client_dict['swarms']:
            if swarm['state'] == 'success':
                success_swarm = swarm
                break
        if not success_swarm:
            raise Exception("No swarm in success state found")

        # Find a node in the swarm
        swarm_id = success_swarm['id']
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] == swarm_id:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No node in swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")

        client.swarm.update(**update_dict)

        self.assertEqual(update_dict['default_addr_pool'], client.swarm.attrs['DefaultAddrPool'])
        self.assertEqual(update_dict['subnet_size'], client.swarm.attrs['SubnetSize'])
        # data_path_addr - Not Sure of Mapping
        # self.assertEqual(update_dict['data_path_addr'], client.swarm.attrs['DataPathAddr'])
        self.assertEqual(update_dict['task_history_retention_limit'], client.swarm.attrs['Spec']['TaskHistoryRetentionLimit'])
        self.assertEqual(update_dict['snapshot_interval'], client.swarm.attrs['Spec']['Raft']['SnapshotInterval'])
        self.assertEqual(update_dict['keep_old_snapshots'], client.swarm.attrs['Spec']['Raft']['KeepOldSnapshots'])
        self.assertEqual(update_dict['log_entries_for_slow_followers'], client.swarm.attrs['Spec']['Raft']['LogEntriesForSlowFollowers'])
        self.assertEqual(update_dict['heartbeat_tick'], client.swarm.attrs['Spec']['Raft']['HeartbeatTick'])
        self.assertEqual(update_dict['election_tick'], client.swarm.attrs['Spec']['Raft']['ElectionTick'])
        self.assertEqual(update_dict['dispatcher_heartbeat_period'], client.swarm.attrs['Spec']['Dispatcher']['HeartbeatPeriod'])
        self.assertEqual(update_dict['node_cert_expiry'], client.swarm.attrs['Spec']['CAConfig']['NodeCertExpiry'])
        self.assertEqual(update_dict['external_ca'], client.swarm.attrs['Spec']['CAConfig']['ExternalCAs'])
        self.assertEqual(update_dict['name'], client.swarm.attrs['Spec']['Name'])
        self.assertEqual(update_dict['labels'], client.swarm.attrs['Spec']['Labels'])
        self.assertEqual(update_dict['signing_ca_cert'], client.swarm.attrs['Spec']['CAConfig']['SigningCACert'])
        self.assertEqual(update_dict['signing_ca_key'], client.swarm.attrs['Spec']['CAConfig']['SigningCAKey'])
        # ca_force_rotate - Not sure what this maps too
        # self.assertEqual(update_dict['ca_force_rotate'], client.swarm.attrs['Spec']['CAConfig']['ForceRotate'])
        self.assertEqual(update_dict['autolock_managers'], client.swarm.attrs['Spec']['EncryptionConfig']['AutoLockManagers'])
        self.assertEqual(update_dict['log_driver'], client.swarm.attrs['Spec']['TaskDefaults']['LogDriver'])


    def test_update_token_rotation(self):
        """
        Test that update function rotates tokens
        """
        update_dict = {
            "rotate_worker_token": True,
            "rotate_manager_token": True,
            "rotate_manager_unlock_key": True,
        }

         # Find a swarm that is in a success state
        success_swarm = None
        validate_swarm = None
        for swarm in self.client_dict['swarms']:
            if swarm['state'] == 'success':
                success_swarm = swarm
                validate_swarm = copy.deepcopy(swarm)
                break
        if not success_swarm:
            raise Exception("No swarm in success state found")

        # Find a node in the swarm
        swarm_id = success_swarm['id']
        node_dict = None
        for node in self.client_dict['nodes']:
            if node['swarm'] == swarm_id:
                node_dict = node
                break
        if not node_dict:
            raise Exception("No node in swarm found")

        ip_address = node_dict['attrs']['Status']['Addr']
        client = self.mock_client.DockerClient(base_url=f"tcp://{ip_address}:2375")

        client.swarm.update(**update_dict)

        self.assertNotEqual(client.swarm.attrs['JoinTokens']['Worker'], validate_swarm['attrs']['JoinTokens']['Worker'])
        self.assertNotEqual(client.swarm.attrs['JoinTokens']['Manager'], validate_swarm['attrs']['JoinTokens']['Manager'])
        self.assertNotEqual(client.swarm.get_unlock_key()['UnlockKey'], validate_swarm['UnlockKey'])
        self.assertEqual(client.swarm.attrs['JoinTokens'], client.swarm._client_dict_entry()['attrs']['JoinTokens'])
        self.assertEqual(client.swarm.get_unlock_key()['UnlockKey'], client.swarm._client_dict_entry()['UnlockKey'])