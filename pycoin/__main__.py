import pycoin.network.node

node = pycoin.network.node.BaseNode(("127.0.0.1", 8888))
node.serve_forever()
