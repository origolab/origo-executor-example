from executor.worker.decryptor.decryptor import Decryptor


class NullDecryptor(Decryptor):
    """
    Null decryptor, this is a fake decryption util which only return the original data.
    """
    def __init__(self):
        """
        Init NullDecryptor.
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
        return encrypted_data
