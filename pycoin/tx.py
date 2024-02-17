import pycoin.utils as utils
from pycoin.logs import logger
import json
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from dataclasses import dataclass


@dataclass
class Tx:
    sender: RSA.RsaKey  # Sender public key
    receiver: RSA.RsaKey  # Receiver public key
    amount: int  # Amount
    timestamp: int  # Timestamp
    signature: bytes = None  # Signature

    _json = ['sender', 'receiver', 'amount', 'timestamp', 'signature']

    def sign(self, key: RSA.RsaKey) -> bytes | None:
        """
        Sign the transaction using the provided key.

        Args:
            key (RSA.RsaKey): The private key used for signing.

        Returns:
            bytes: The signature of the transaction.
        """
        if not key.has_private():
            raise ValueError("The provided key is not a private key.")
        if key.public_key() != self.sender:
            raise ValueError(
                "The provided key does not match the sender's public key.")
        try:
            sig_scheme = pkcs1_15.new(key)
            self.signature = sig_scheme.sign(self.__hash())
            return self.signature
        except Exception as e:
            logger.error(f'Error occurred while signing the transaction: {e}')
            return None

    def isSigned(self) -> bool:
        """
        Check if the transaction is signed.

        Returns:
            bool: True if the transaction is signed, False otherwise.
        """
        if isinstance(self.signature, bytes) and len(self.signature) > 0:
            return True
        else:
            return False

    def validateSignature(self) -> bool:
        """
            Validate the signature of the transaction.

            This method verifies the signature of the transaction using the sender's public key and the provided signature.

            Raises:
            - ValueError: If the transaction is not signed.

            Returns:
            - bool
                True if the signature is valid, False otherwise.
        """
        if not self.isSigned():
            raise ValueError("The transaction is not signed.")

        sig_scheme = pkcs1_15.new(self.sender)
        sig_scheme.verify(self.__hash(), self.signature)
        return True

    def toJSON(self):
        return json.dumps(self, cls=utils.Encoder, sort_keys=True)

    def __hash(self):
        dct = {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'timestamp': self.timestamp
        }
        json_ecoded = json.dumps(dct, cls=utils.Encoder, sort_keys=True)

        return SHA256.new(json_ecoded.encode())

    @property
    def hash(self) -> bytes:
        return self.__hash().digest()
