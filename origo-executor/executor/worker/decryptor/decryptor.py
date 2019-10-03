from abc import ABC
from abc import abstractmethod


class Decryptor(ABC):
    """
    Base class for decrypting encrypted data.
    """
    @abstractmethod
    def decrypt(self, encrypted_data):
        """
        Decrypt encrypted data.
        Args:
            encrypted_data: encrypted data.

        Returns:
            Decrypted data from the input encrypted data.

        """
        raise NotImplementedError('Abstract method, not implemented yet')
