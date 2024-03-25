from Crypto.PublicKey import RSA
from typing import get_type_hints, get_args, get_origin
from .block import Block
import json


class BlockchainDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, *args, **kwargs)

    def decode_class(self, value: any, cls) -> any:
        cls_origin = get_origin(cls) or cls
        if issubclass(cls, bytes):
            if not type(value) == str:
                raise json.JSONDecodeError('Expected bytes')
            bval = bytes.fromhex(value)
            return cls(bval)

        if cls is RSA.RsaKey:
            return RSA.import_key(bytes.fromhex(value))

        if cls_origin in {list, tuple}:
            if not isinstance(value, list):
                raise json.JSONDecodeError('Expected list')
            sub_hint = get_args(cls)[0]
            result = []
            for item in value:
                result.append(self.decode_class(item, cls=sub_hint))
            return result

        if isinstance(value, dict):
            class_hints = get_type_hints(cls)
            kwargs = {}
            for key, val in value.items():
                hint = class_hints[key]
                kwargs[key] = self.decode_class(val, cls=hint)
            obj = cls(**kwargs)
            return obj

        return value

    def decode(self, s):
        dct = super(BlockchainDecoder, self).decode(s)
        result = {}

        for key, value in dct.items():
            result[key] = self.decode_class(value, cls=Block)

        return result
