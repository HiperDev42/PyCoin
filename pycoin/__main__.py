from pycoin.network.node import Node

HOST = '127.0.0.1'
PORT = 8888

node = Node(HOST, PORT)
node.start()
