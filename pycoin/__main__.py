import socket


NODE_SERVER_BIND = '0.0.0.0'
NODE_SERVER_PORT = 4000


if __name__ == '__main__':
    node_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    node_server.bind((NODE_SERVER_BIND, NODE_SERVER_PORT))
    node_server.listen()

    _, port = node_server.getsockname()
    print(f"PyCoin node server started on port {port}")

    node_server.close()
