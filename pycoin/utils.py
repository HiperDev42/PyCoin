import json
from Crypto.PublicKey import RSA


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.hex()
        if isinstance(obj, RSA.RsaKey):
            return obj.export_key().hex()

        if hasattr(obj, '_json'):
            jsonDict = {}
            for field in obj._json:
                jsonDict[field] = getattr(obj, field)
            return jsonDict
        return obj.__dict__
