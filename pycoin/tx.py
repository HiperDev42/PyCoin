import pycoin.utils as utils
from pycoin.logs import logger
import json
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


class Tx:
    sender: RSA.RsaKey  # Sender public key
    receiver: RSA.RsaKey  # Receiver public key
    amount: int  # Amount
    timestamp: int  # Timestamp

    def __init__(self, sender: RSA.RsaKey, receiver: RSA.RsaKey, amount: int, timestamp: int) -> None:
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp

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
        try:
            sig_scheme = pkcs1_15.new(key)
            signature = sig_scheme.sign(self.__hash())
            return signature
        except Exception as e:
            logger.error(f'Error occurred while signing the transaction: {e}')
            return None

    def verifySignature(self, signature: bytes) -> bool:
        """
            Verify the signature of the transaction.

            This method verifies the signature of the transaction using the sender's public key and the provided signature.

            Parameters:
            - signature: bytes
                The signature of the transaction.

            Raises:
            - ValueError: If the signature parameter is empty.
            - TypeError: If the signature is not of type `bytes`.

            Returns:
            - bool
                True if the signature is valid, False otherwise.
        """
        if not isinstance(signature, bytes):
            raise TypeError("The signature must be of type bytes.")
        if not signature:
            raise ValueError("The signature parameter cannot be empty.")

        try:
            sig_scheme = pkcs1_15.new(self.sender)
            sig_scheme.verify(self.__hash(), signature)
            return True
        except ValueError:
            return False

    def toJSON(self):
        return json.dumps(self, cls=utils.Encoder, sort_keys=True)

    def __hash(self):
        return SHA256.new(self.toJSON().encode())

    @property
    def hash(self) -> bytes:
        return self.__hash().digest()
