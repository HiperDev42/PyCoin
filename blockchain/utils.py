import hashlib


def get_merkle_root(tree: list):
    if len(tree) == 0:
        return hashlib.sha256(b'').digest()
    cpy = tree.copy()
    while len(cpy) > 1:
        if len(cpy) % 2 == 1:
            cpy.append(cpy[-1])
        new_tree = []
        for i in range(len(cpy)):
            h1 = cpy[i]
            h2 = cpy[i+1]
            hash = hashlib.sha256(h1+h2).digest()
            new_tree.append(hash)
        cpy = new_tree
    return cpy[0]
