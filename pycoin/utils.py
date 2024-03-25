import json
from Crypto.Hash import RIPEMD160, SHA256
from Crypto.PublicKey import RSA


def hash160(data: bytes):
    return RIPEMD160.new(SHA256.new(data).digest()).digest()


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if issubclass(type(obj), bytes):
            return obj.hex()
        if isinstance(obj, RSA.RsaKey):
            return obj.export_key('DER').hex()

        if hasattr(obj, '_json'):
            jsonDict = {}
            for field in obj._json:
                jsonDict[field] = getattr(obj, field)
            return jsonDict
        return obj.__dict__
