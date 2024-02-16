import json


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.hex()
        return obj.__dict__
