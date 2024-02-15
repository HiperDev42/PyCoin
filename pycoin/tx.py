import json
from hashlib import sha256


class Tx:
    sender: str
    receiver: str
    amount: int
    timestamp: int

    def __init__(self) -> None:
        pass

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    @property
    def hash(self) -> bytes:
        return sha256(self.toJSON().encode()).digest()
