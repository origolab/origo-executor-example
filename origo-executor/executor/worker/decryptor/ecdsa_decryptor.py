from executor.worker.decryptor.decryptor import Decryptor


class ECDSADecryptor(Decryptor):
    """
    ECDSA based decryption util.
    """
    def __init__(self):
        """
        Init ECDSADecryptor.
        """
        pass

    def decrypt(self, encrypted_data):
        """
        Decrypt encrypted data.
        Args:
            encrypted_data: encrypted data.

        Returns:
            Decrypted data from the input encrypted data.

        """
        raise NotImplementedError('Abstract method, not implemented yet')
