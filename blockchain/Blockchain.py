from . import Block
from .Account import Account
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
            return []
        chain = [bytes.fromhex(h) for h in encoded_chain]
        return chain
    
    def set(self, block: Block):
        hash = block.hash().hex()
        self.db.set(hash, block.to_json())
    
    def get(self, key):
        return self.db.get(key)


class Blockchain:
    db: Database = None

    def __init__(self) -> None:
        self.db = Database()
        self.chain = self.db.get_chain()

        self.validate_chain()

    def last_hash(self):
        if len(self.chain) > 0:
            return self.chain[-1]
        return b'\x00' * 32
    
    def get_block(self, hash: bytes):
        block_json = self.db.get(hash.hex())
        block = Block.from_json(block_json)
        return block
    
    def get_balance(self, account: Account):
        balance = 0
        for hash in self.chain:
            block = self.get_block(hash)
            for tx in block.txs:
                if tx.src == account:
                    balance -= tx.amount
                if tx.dst == account:
                    balance += tx.amount
        
        return balance
    
    def append(self, block: Block):
        if not block.validate():
            raise Exception('block not valid')

        hash = block.hash()
        self.chain.append(hash)
        self.db.set_chain(self.chain)
        self.db.set(block)
    
    def validate_chain(self):
        for block_hash in self.chain:
            block = self.get_block(block_hash)
            if not block.validate():
                raise Exception('Chain corrupted')
    
    def flush(self):
        self.db.set_chain(self.chain)
        self.db._dump()
