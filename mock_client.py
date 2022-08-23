"""
mock_client is a temporary db to mock the Docker API in unit tests.
"""

import sqlite3
import json



class MockClient:

    def __init__(self):
        self._con = sqlite3.connect(':memory:')
        self._cur = self._con.cursor()

    def build_from_file(self, filename):
        """
        Reads in a JSON file of a standard format and populates the database for testing
        """
        # Read in the JSON file
        f = open(filename)
        table_dict = json.load(f)

        if "swarms" in table_dict:
            # Build Swarm Table if Needed
            self._cur.execute('''CREATE TABLE swarms (
                              id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                              swarm_id TEXT NOT NULL, 
                              attrs TEXT)''')
            
            # Populate Swarm Table from Entries
            for swarm in table_dict['swarms']:
                self._cur.execute('''INSERT INTO SWARMS(swarm_id, attrs) VALUES (?,?)''', (swarm['ID'],json.dumps(swarm)))

            self._con.commit() 

        
        # Build Node Table if Needed
        if "nodes" in table_dict:
            # Build the Node Table if Needed
            self._cur.execute('''CREATE TABLE nodes (
                              id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                              node_id TEXT, 
                              node_name TEXT, 
                              attrs TEXT, 
                              state TEXT,
                              swarm_id  INTEGER,
                              FOREIGN KEY (id)
                              REFERENCES swarms (id))''')

            for node in table_dict['nodes']:
                # Validate attrs dict

                # Get swarm_id
                swarm_id = self._cur.execute('''SELECT id from swarms WHERE swarm_id = (?)''', (node['swarm_id'],)).fetchone()
                print(node['swarm_id'])
                print(swarm_id)
                # Build Node Tupple
                node_tup = (node['attrs']['ID'], node['attrs']['Spec']['Name'], json.dumps(node['attrs']), node['state'], swarm_id[0])
                # Insert Node into Table
                self._cur.execute('''INSERT INTO NODES(node_id, node_name, attrs, state, swarm_id) VALUES (?,?,?,?,?)''', node_tup)

            self._con.commit()

            return True

    def close(self):
        """
        Simulates closing the connect by destroying the test(temp) database
        """
        self._con.close()

