from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from executor.utils.data_utils import DataUtils
from executor.worker.decryptor.decryptor import Decryptor


class RSADecryptor(Decryptor):
    """
    Decryptor based on RSA util.
    """
    def __init__(self, pem_path):
        """
        Init RSADecryptor.
        """
        key_file = open(pem_path, 'rb')
        private_key = RSA.importKey(key_file.read())
        self.__decryptor = PKCS1_v1_5.new(private_key)

    def decrypt(self, encrypted_data):
        """
        Decrypt encrypted data.
        Args:
            encrypted_data: encrypted data represented as integer.

        Returns:
            Decrypted data from the input encrypted data.

        """

        encrypted_bytes = DataUtils.int2bytes(encrypted_data, 128)
        re = self.__decryptor.decrypt(encrypted_bytes, None)
        return DataUtils.bytes2int(re)
