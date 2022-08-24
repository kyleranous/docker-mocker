"""
mock_docker is a temporary db to mock the Docker API in unit tests.
"""

import sqlite3
import json
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
                self._active_server = node
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
            self._swarm = node_dict['swarm']
            self._state = node_dict['state']
            self.mock_docker = mock_docker


        
            
            
