from . import Block
import hashlib
import pickledb
import json


class Database:
    filepath: str
    db: pickledb.PickleDB

    def __init__(self, filepath='./blockchain.db') -> None:
        self.filepath = filepath
        self._load()
    
    def _load(self):
        try:
            self.db = pickledb.load(self.filepath, auto_dump=True)
            return self.db
        except json.JSONDecodeError as e:
            print('Database corrupted')
            with open(self.filepath, 'w') as file:
                file.write('{}')
                file.close()
            self.db = pickledb.load(self.filepath, auto_dump=True)
            return self.db
            
    
    def _dump(self):
        return self.db.dump()

    def set_chain(self, chain):
        encoded_chain = [h.hex() for h in chain]
        self.db.set('chain', encoded_chain)
    
    def get_chain(self):
        encoded_chain = self.db.get('chain')
        if not encoded_chain:
            return False
        chain = [bytes.fromhex(h) for h in encoded_chain]
        return chain
    
    def set(self, block: Block):
        hash = block.hash().hex()
        self.db.set(hash, block.to_json())
    
    def get(self, key):
        return self.db.get(key)


class Blockchain:
    db: Database = None
    genesis = Block(
        b"\xe3\xb0\xc4B\x98\xfc\x1c\x14\x9a\xfb\xf4\xc8\x99o\xb9$'\xaeA\xe4d\x9b\x93L\xa4\x95\x99\x1bxR\xb8U",
        nonce=39,
    )

    def __init__(self) -> None:
        self.db = Database()
        self.chain = self.db.get_chain()
        print(self.chain)
        if not self.chain:
            self.chain = []
            self.append(Blockchain.genesis)

    def last_hash(self):
        return self.chain[-1]
    
    def get_block(self, idx: int):
        hash = self.chain[idx].hex()
        block_json = self.db.get(hash)
        block = Block.from_json(block_json)
        return block

    def append(self, block: Block):
        hash = block.hash()
        self.chain.append(hash)
        self.db.set_chain(self.chain)
        self.db.set(block)
    
    def dump(self):
        print(self.chain)
        self.db._dump()
