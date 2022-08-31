"""
mock_docker is a temporary db to mock the Docker API in unit tests.
"""

import docker
import random
import string
import json

from validate import validate_swarm_data

class MockDocker:

    def __init__(self, client_dict={}):
        # Validate Swarms in client_dict
        swarm_errors = validate_swarm_data(client_dict['swarms'])
        if len(swarm_errors) > 0:
            raise Exception(f'{json.dumps(swarm_errors, indent=4)}')
            
        # Validate Nodes in client_dict


        self._active_server = None
        self._client_dict = client_dict
        self.nodes = MockDocker.Nodes(self)
        #self.swarm = MockDocker.Swarm()

    def DockerClient(self, base_url):
        ip_address = base_url.split(":")[1].strip("/")
        for node in self._client_dict['nodes']:
            if node['attrs']['Status']['Addr'] == ip_address:
                # Set Active Server
                self._active_server = node
                # Load Swarm based on Active Server
                self.swarm = MockDocker.Swarm(self)
                return self

    class Nodes:

        def __init__(self, mock_docker):
            self.mock_docker = mock_docker

        def get(self, id_or_name):
            # Verify a connection has been established and node is part of swarm
            if self.mock_docker._active_server is None or self.mock_docker._active_server['swarm'] is None:
                raise docker.errors.APIError("No connection established")

            # Search through Nodes that belong to the same swarm
            for node in self.mock_docker._client_dict['nodes']:
                if node['swarm'] == self.mock_docker._active_server['swarm']:
                    # Check if id_or_name matches current node
                    if node['attrs']['ID'] == id_or_name or node['attrs']['Spec']['Name'] == id_or_name:
                        return MockDocker.Node(node, self.mock_docker)

            # No match is found Raise APIError
            raise docker.errors.APIError(f"No Node with id or name {id_or_name} found")

        def list(self, **kwargs):
            # Verify a connection has been established and node is part of swarm
            if self.mock_docker._active_server is None or self.mock_docker._active_server['swarm'] is None:
                raise docker.errors.APIError("No connection established")

            # Check if filters are passed
            filters = kwargs.get('filters', None)
            # Search through Nodes that belong to the same swarm
            nodes = []
            for node in self.mock_docker._client_dict['nodes']:
                if node['swarm'] == self.mock_docker._active_server['swarm']:
                    if filters:
                        if 'id' in filters.keys():
                            if filters['id'] not in node['attrs']['ID']:
                                continue
                        if 'name' in filters.keys():
                            if filters['name'] not in node['attrs']['Spec']['Name']:
                                continue
                        if 'membership' in filters.keys():
                            # Need to figure out how to do this one
                            pass
                        if 'role' in filters.keys():
                            if filters['role'] != node['attrs']['Spec']['Role']:
                                continue

                    nodes.append(MockDocker.Node(node, self.mock_docker))

            return nodes

    class Node:

        def __init__(self, node_dict, mock_docker):
            self.attrs = node_dict['attrs']
            self.id = node_dict['attrs']['ID']
            self.short_id = node_dict['attrs']['ID'][:10]
            self.version = node_dict['attrs']['Version']['Index']
            self._swarm = node_dict['swarm']
            self._state = node_dict['state']
            self.mock_docker = mock_docker

        def reload(self):
            """
            Simulates docker.Node.reload() by adjusting the state of the node
            """
            if self._state == 'fail':
                self._state = 'reload'

        def update(self, node_spec):
            """
            Simulates the update function by adjusting the node entry in MockDocker
            """
            # Check to see if node is in a fail state
            if self._state == 'fail':
                raise docker.errors.APIError("Failed to update node")

            # Update the node Spec
            self.attrs['Spec']['Availability'] = node_spec.get('Availability')
            self.attrs['Spec']['Role'] = node_spec.get('Role')
            self.attrs['Spec']['Labels'] = node_spec.get('Labels')
            self.attrs['Spec']['Name'] = node_spec.get('Name')

            # Update the nodes library in MockDocker
            for node in self.mock_docker._client_dict['nodes']:
                if node['attrs']['ID'] == self.id:
                    node['attrs']['Spec'] = self.attrs['Spec']

            if self._state == 'reload':
                self._state = 'fail'

            return True


    class Swarm:

        def __init__(self, mock_docker):
            self.mock_docker = mock_docker
            # Find which Swarm this node belongs to
            self._swarm_id = mock_docker._active_server['swarm']
            self.attrs = None
            for swarm in mock_docker._client_dict['swarms']:
                if swarm['id'] == self._swarm_id:
                    self.attrs = swarm.get('attrs')
                    self.version = self.attrs.get('Version').get('Index')
                    self._state = swarm.get('state')
                    self._unlock_key = swarm.get('UnlockKey')
                    break
            

        def get_unlock_key(self):
            """
            Simulates the get_unlock_key function by returning a dictionary with "UnlockKey"
            """
            key_dict = {
                "UnlockKey": self._unlock_key
            }
            return key_dict

        def init(self, **kwargs):
            """
            Initializes a new swarm from a node not a part of a swarm
            """
            advertise_addr = kwargs.get('advertise_addr', None)
            listen_addr = kwargs.get('listen_addr', '0.0.0.0:2377')
            force_new_cluster = kwargs.get('force_new_cluster', False)
            default_addr_pool = kwargs.get('default_addr_pool', None)
            subnet_size = kwargs.get('subnet_size', None)
            data_path_addr = kwargs.get('data_path_addr')
            task_history_retention_limit = kwargs.get('task_history_retention_limit')
            snapshot_interval = kwargs.get('snapshot_interval')
            keep_old_snapshots = kwargs.get('keep_old_snapshots')
            log_entries_for_slow_followers = kwargs.get('log_entries_for_slow_followers')
            heartbeat_tick = kwargs.get('heartbeat_tick')
            election_tick = kwargs.get('election_tick')
            dispatcher_heartbeat_period = kwargs.get('dispatcher_heartbeat_period')
            node_cert_expiry = kwargs.get('node_cert_expiry')
            external_ca = kwargs.get('external_ca')
            name = kwargs.get('name')
            labels = kwargs.get('labels', {})
            signing_ca_cert = kwargs.get('signing_ca_cert')
            signing_ca_key = kwargs.get('signing_ca_key')
            ca_force_rotate = kwargs.get('ca_force_rotate')
            autolock_managers = kwargs.get('autolock_managers', False)
            log_driver = kwargs.get('log_driver')

            if self._swarm_id is not None:
                raise docker.errors.APIError("This node is already part of a swarm")            

            self._swarm_id = self._generate_token(16)
            self._unlock_key = self._generate_token(64)
            
            self.state = "success"
            self.mock_docker._active_server['swarm'] = self._swarm_id

            attrs_dict = {
                "ID": "swarm_2",
                "Version": {
                    "Index": 373532
                },
                "CreatedAt": "2016-08-18T10:44:24.496525531Z",
                "UpdatedAt": "2017-08-09T07:09:37.632105588Z",
                "Spec": {
                    "Name": name,
                    "Labels": labels,
                    "Orchestration": {
                        "TaskHistoryRetentionLimit": task_history_retention_limit
                    },
                    "Raft": {
                        "SnapshotInterval": snapshot_interval,
                        "KeepOldSnapshots": keep_old_snapshots,
                        "LogEntriesForSlowFollowers": log_entries_for_slow_followers,
                        "ElectionTick": election_tick,
                        "HeartbeatTick": heartbeat_tick
                    },
                    "Dispatcher": {
                        "HeartbeatPeriod": dispatcher_heartbeat_period
                    },
                    "CAConfig": {
                        "NodeCertExpiry": node_cert_expiry,
                        "ExternalCAs": external_ca,
                        "SigningCACert": signing_ca_cert,
                        "SigningCAKey": signing_ca_key,
                        "ForceRotate": ca_force_rotate
                    },
                    "EncryptionConfig": {
                        "AutoLockManagers": autolock_managers
                    },
                    "TaskDefaults": {
                        "LogDriver": log_driver
                    }
                },
                "TLSInfo": {
                    "TrustRoot": "",
                    "CertIssuerSubject": "",
                    "CertIssuerPublicKey": ""
                },
                "RootRotationInProgress": False,
                "DataPathPort": 4789,
                "DefaultAddrPool": default_addr_pool,
                "SubnetSize": subnet_size,
                "JoinTokens": {
                    "Worker": self._generate_token(32),
                    "Manager": self._generate_token(32)
                }
            }

            swarm_dict = {
                "id": self._swarm_id,
                "state": self.state,
                "UnlockKey": self._unlock_key,
                "attrs": attrs_dict
            }
            self.attrs = attrs_dict
            self.mock_docker._client_dict['swarms'].append(swarm_dict)
            return self._swarm_id


        def join(self, **kwargs):
            """
            Allows node not in a swarm to join an existing swarm
            """
            remote_addrs = kwargs.get('remote_addrs')
            join_token = kwargs.get('join_token')
            listen_addr = kwargs.get('listen_addr', '0.0.0.0:2377')
            advertise_addr = kwargs.get('advertise_addr', None)
            data_path_addr = kwargs.get('data_path_addr', advertise_addr)

            # Check if client is already a member of a swarm
            if self.mock_docker._active_server['swarm'] is not None or join_token is None:
                raise docker.errors.APIError("Client is already a member of a swarm")

            # find swarm that is being joined
            swarm_id = None
            for node in self.mock_docker._client_dict['nodes']:
                if node['attrs']['Status']['Addr'] in remote_addrs:
                    if node['swarm'] is not None:
                        swarm_id = node['swarm']
                        break
            if swarm_id is None:
                raise docker.errors.APIError("Swarm not found")

            join_swarm = None
            for swarm in self.mock_docker._client_dict['swarms']:
                if swarm['id'] == swarm_id:
                    join_swarm = swarm
                    break
            if join_swarm is None:
                raise docker.errors.APIError("Swarm not found")

            if join_token == join_swarm['attrs']['JoinTokens']['Manager']:
                self.mock_docker._active_server['swarm'] = swarm_id
                self.mock_docker._active_server['attrs']['Spec']['Role'] = 'manager'
                return True
            
            if join_token == join_swarm['attrs']['JoinTokens']['Worker']:
                self.mock_docker._active_server['swarm'] = swarm_id
                self.mock_docker._active_server['attrs']['Spec']['Role'] = 'worker'
                return True

            raise docker.errors.APIError("Join token is invalid")
            

        def leave(self, force=False):
            """
            Request Node to leave the swarm, will fail if node is manager unless
            force is set to true
            """
            if self.mock_docker._active_server['swarm'] is None:
                raise docker.errors.APIError("Node is not part of a swarm")
            
            if self.mock_docker._active_server['attrs']['Spec']['Role'] == 'manager' and not force:
                raise docker.errors.APIError("Node is a manager and force is not set")

            self.mock_docker._active_server['swarm'] = None
            self.mock_docker._active_server['attrs']['Spec']['Role'] = None
            self._swarm_id = None
            self.attrs = None
            self.version = None
            self._state = None
            self._unlock_key = None        
            return True

        def unlock(self, key):
            """
            Unlock Swarm if passed Key is valid
            """
            # Check that key is a string
            if not isinstance(key, str):
                raise docker.errors.InvalidArgument("key must be a string")

            if key == self._unlock_key:
                if self._state == "locked":
                    self._state = "success"
                    return True

            raise docker.errors.APIError("Invalid unlock key")

        def update(self, **kwargs):
            """
            Update Swarm Configurations
            """
            default_addr_pool = kwargs.get('default_addr_pool', None)
            subnet_size = kwargs.get('subnet_size', None)
            data_path_addr = kwargs.get('data_path_addr')
            task_history_retention_limit = kwargs.get('task_history_retention_limit')
            snapshot_interval = kwargs.get('snapshot_interval')
            keep_old_snapshots = kwargs.get('keep_old_snapshots')
            log_entries_for_slow_followers = kwargs.get('log_entries_for_slow_followers')
            heartbeat_tick = kwargs.get('heartbeat_tick')
            election_tick = kwargs.get('election_tick')
            dispatcher_heartbeat_period = kwargs.get('dispatcher_heartbeat_period')
            node_cert_expiry = kwargs.get('node_cert_expiry')
            external_ca = kwargs.get('external_ca')
            name = kwargs.get('name')
            labels = kwargs.get('labels', {})
            signing_ca_cert = kwargs.get('signing_ca_cert')
            signing_ca_key = kwargs.get('signing_ca_key')
            ca_force_rotate = kwargs.get('ca_force_rotate')
            autolock_managers = kwargs.get('autolock_managers', False)
            log_driver = kwargs.get('log_driver')

            rotate_worker_token = kwargs.get('rotate_worker_token', False)
            rotate_manager_token = kwargs.get('rotate_manager_token', False)
            rotate_manager_unlock_key = kwargs.get('rotate_manager_unlock_key', False)

            # Check if Swarm is in Fail State, if so, raise error
            if self._state == 'fail':
                raise docker.errors.APIError("Update Failed")

            for swarm in self.mock_docker._client_dict['swarms']:
                if swarm['id'] == self._swarm_id:
                    # Update attrs with new information
                    if default_addr_pool is not None: self.attrs['DefaultAddrPool'] = default_addr_pool
                    if subnet_size is not None: self.attrs['SubnetSize'] = subnet_size
                    #if data_path_addr is not None: self.attrs['DataPathAddr'] = data_path_addr
                    if task_history_retention_limit is not None: self.attrs['Spec']['TaskHistoryRetentionLimit'] = task_history_retention_limit
                    if snapshot_interval is not None: self.attrs['Spec']['Raft']['SnapshotInterval'] = snapshot_interval
                    if keep_old_snapshots is not None: self.attrs['Spec']['Raft']['KeepOldSnapshots'] = keep_old_snapshots
                    if log_entries_for_slow_followers is not None: self.attrs['Spec']['Raft']['LogEntriesForSlowFollowers'] = log_entries_for_slow_followers
                    if heartbeat_tick is not None: self.attrs['Spec']['Raft']['HeartbeatTick'] = heartbeat_tick
                    if election_tick is not None: self.attrs['Spec']['Raft']['ElectionTick'] = election_tick
                    if dispatcher_heartbeat_period is not None: self.attrs['Spec']['Dispatcher']['HeartbeatPeriod'] = dispatcher_heartbeat_period
                    if node_cert_expiry is not None: self.attrs['Spec']['CAConfig']['NodeCertExpiry'] = node_cert_expiry
                    if external_ca is not None: self.attrs['Spec']['CAConfig']['ExternalCAs'] = external_ca
                    if name is not None: self.attrs['Spec']['Name'] = name
                    if labels is not None: self.attrs['Spec']['Labels'] = labels
                    if signing_ca_cert is not None: self.attrs['Spec']['CAConfig']['SigningCACert'] = signing_ca_cert
                    if signing_ca_key is not None: self.attrs['Spec']['CAConfig']['SigningCAKey'] = signing_ca_key
                    if ca_force_rotate is not None: self.attrs['Spec']['CAConfig']['ForceRotate'] = ca_force_rotate
                    if autolock_managers is not None: self.attrs['Spec']['AutolockManagers'] = autolock_managers
                    if log_driver is not None: self.attrs['Spec']['TaskDefaults']['LogDriver'] = log_driver

                    # Update tokens if rotation booleans are set
                    if rotate_worker_token:
                        new_token = self._generate_token()
                        self.attrs['JoinTokens']['Worker'] = new_token
                        #swarm['attrs']['JoinTokens']['Worker'] = new_token

                    if rotate_manager_token:
                        new_token = self._generate_token()
                        self.attrs['JoinTokens']['Manager'] = new_token
                        #swarm['attrs']['JoinTokens']['Manager'] = new_token

                    if rotate_manager_unlock_key:
                        new_token = self._generate_token(64)
                        self._unlock_key = new_token
                        swarm['UnlockKey'] = new_token
                    break

            # Reset state to fail if reload
            if self._state == 'reload':
                self._state = 'fail'
            
        def reload(self):
            if self._state == 'fail':
                self._state = 'reload'
            return True

        def _generate_token(self, length=32):
            """
            Generate a random token of the specified length
            """
            return ''.join(random.choice(string.ascii_uppercase + string.ascii_letters + string.digits) for _ in range(length))
            
        def _client_dict_entry(self):
            for swarm in self.mock_docker._client_dict['swarms']:
                if swarm['id'] == self._swarm_id:
                    return swarm
            return None