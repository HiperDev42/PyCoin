import json
from Crypto.PublicKey import RSA


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.hex()
        if isinstance(obj, RSA.RsaKey):
            return obj.export_key().hex()
        return obj.__dict__
