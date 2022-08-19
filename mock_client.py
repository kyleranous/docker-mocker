"""
MockClient class used to spoof Docker Python SDK client classes for unit testing.
"""
import json

from docker.errors import APIError



class MockClient:
    """
    MockClient is a class for spoofing the Docker Python SDK for unit testing.
    """
    def __init__(self):
        self.nodes = MockClient.TestNodes()

    def load_from_file(self, file_name):
        """
            Creates a MockClient object with Nodes and a swarm from a JSON File
        """
        f = open(file_name)
        client_dict = json.load(f)
        if client_dict and len(self.nodes.node_list) == 0:
            # Create Nodes
            for node in client_dict.get('nodes'):
                self.nodes.add_node(node)
            
            return True
        
        return False
    class TestNodes:
        """
        
        """
        node_list = []

        def add_node(self, node_dict):
            """
            """
            self.node_list.append(MockClient.Node(node_dict))

        def get(self, node_id):
            """
            Returns a Node object from either a node id or name.
            Raises APIError if no node is found.
            """
            for node in self.node_list:
                if node.id == node_id or node.attrs['Spec']['Name'] == node_id:
                    return node

            # If no node is found with matching id raise docker.errors.APIError
            raise APIError(f"No node found with id or name {node_id}")

        def list(self, filters=None):
            """
            Returns a list of nodes 
            """
            nodes = []
            if filters:
                if 'role' in filters.keys():
                    for node in self.node_list:
                        if node.attrs['Spec']['Role'] == filters['role']:
                            nodes.append(node)

                if 'name' in filters.keys():
                    filtered_nodes = nodes if len(nodes) > 0 else self.node_list
                    for node in filtered_nodes:
                        if filters['name'].lower() in node.attrs['Spec']['Name'].lower():
                            nodes.append(node)

                if 'membership' in filters.keys():
                    filtered_nodes = nodes if len(nodes) > 0 else self.node_list
                    for node in filtered_nodes:
                        # Need to figure out the membership filter
                        pass
                    
                if 'id' in filters.keys():
                    filtered_nodes = nodes if len(nodes) > 0 else self.node_list
                    for node in filtered_nodes:
                        if filters['id'].lower() in node.id.lower():
                            nodes.append(node)

                return nodes
            
            return self.node_list

    class Node:

        def __init__(self, node_dict):

            self.attrs = node_dict
            self.id = node_dict['ID']
            self.short_id = self.id[0:10]
            self.version = self.attrs["Version"]["Index"]
            
        def update(self, node_spec):
            
            if "fail" in self.id:
                #If node is intended to fail, raise docker.errors.APIError
                raise APIError(f"Failed to update node {self.id}")
            
            self.attrs['Spec'] = node_spec
            return True

        def reload(self):
            """
            simulates docker.Client.Node.reload()
            """
            if "noreload" not in self.id:
                self.update_id(self.id.replace('fail', 'reload'))

        def update_id(self, new_id):
            self.id = new_id
            self.short_id = self.id[0:10]
            self.attrs['ID'] = new_id

        def reset_id(self):
            if "noreload" not in self.id:
                new_id = self.id.replace('reload', 'fail')
                self.id = new_id
                self.short_id = self.id[0:10]
                self.attrs['ID'] = new_id

       
            
    


    