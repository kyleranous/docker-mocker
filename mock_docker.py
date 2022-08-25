"""
mock_docker is a temporary db to mock the Docker API in unit tests.
"""

import docker



class MockDocker:

    def __init__(self, client_dict={}):
        # Validate Swarms in client_dict

        # Validate Nodes in client_dict

        #

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
            swarm_id = mock_docker._active_server['swarm']
            self.attrs = None
            for swarm in mock_docker._client_dict['swarms']:
                if swarm['id'] == swarm_id:
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
            pass

        def join(self, **kwargs):
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
            pass

        def unlock(self):
            pass

        def update(self, **kwargs):
            pass

        def reload(self):
            if self._state == 'fail':
                self._state = 'reload'
            return True

