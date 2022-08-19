# Docker Mocker


## Description
Docker Mocker is python package that spoofs the docker SDK for unit testing. 


## Installation
Clone repository and copy into project
Install docker package (if not already installed), MockClient() will pass the expected docker errors to test exception handling.
Import MockClient into unit tests


## Usage

### MockClient()
Create a Json file that defines the needed docker classes (nodes, swarms, volumes, etc.), example JSON file `tests\mockClient.json`. In a unit test define a MockClient object and populate it from the JSON file 
```
test_client = MockClient().load_from_file('[path/to/json].json')
```
Write the unit tests passing the MockClient() object in place of the docker client object.

### MockClient.nodes
`MockClient.nodes` is an instance of `MockClient.TestNodes()` that is generated automatically when a `MockClient()` object is initialized. The `TestNodes()` subclass holds a list of `MockClient.Node()` objects, the `get()` and `list()` functions that are replicas of `docker.client.nodes.get()` and `docker.client.nodes.list()` functions, and a `add_node()` function that will add a `MockClient.Node()` object to the list. 

### MockClient.Node
`MockClient.Node` is an object that contains the rest of the `docker.client.nodes` functions. `MockClient.Node.attrs` is a dictionary object of the same format as `docker.client.nodes.attrs`. `MockClient.Node.update()` functions like `docker.client.nodes.update()`, however it will always succeed unless `fail` is in the Node ID, then it will raise a `docker.errors.APIError`. Calling `reload` on a node with `fail` in the Node ID, will change the `fail` to `reload`. If follow on testing is needed with that node before it get's recreated, the ID will need to be updated to replace `reload` with `fail`. However, ending a node_id with `no_reload` will force `reload()` to fail.

```python
# node.id = 'worker_fail_node'
node.update(node_spec=new_attrs) # Raises APIError because 'fail' in node id
node.reload() # Simulates reloading the version, replaces `fail` in the node id with `reload` node.id = 'worker_reload_node'
node.update(node_spec=new_attrs) # Succeeds

# Reset the node_id for follow on testing
node.reset_id() # node.id = 'worker_fail_node'

# node.id = 'worker_fail_noreload`
node.update(node_spec=new_attrs) # Raises APIError because 'fail' in node id
node.reload() # Makes no change because `noreload` in node id

node.update(node_spec=new_attrs) # Still Raises APIError

node.reset_id() # Does nothing because `noreload` in node id

```


## How to Contribute