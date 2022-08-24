import docker


def client_connect(address):
    """
    Connect to a docker client
    """

    client = docker.DockerClient(base_url=address)
    return client.nodes.get("test_node")