import unittest

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random
from executor.worker.decryptor.rsa_decryptor import RSADecryptor


class EthInterfaceTests(unittest.TestCase):
    def setUp(self):
        # create key pair
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)
        public_key = key.publickey()
        encryptor = PKCS1_OAEP.new(public_key)
        self.__msgs = [
            'i love your',
            'i love blockchain',
            'i love origo',
            'i love dog'
        ]
        self.__encrypted_msgs = self._encrypt_msgs(encryptor, self.__msgs)
        key_str = key.exportKey().decode()
        self.__key_pem = key_str.replace('-----BEGIN RSA PRIVATE KEY-----\n', '')\
            .replace('\n-----END RSA PRIVATE KEY-----', '')
        print(self.__key_pem)

    @staticmethod
    def _encrypt_msgs(encryptor, msgs):
        ret = []
        for msg in msgs:
            ret.append(encryptor.encrypt(msg.encode()))
        return ret

    def test_decrypt(self):
        rsa_decyptor = RSADecryptor(self.__key_pem)
        for i in range(len(self.__msgs)):
            self.assertEqual(self.__msgs[i], rsa_decyptor.decrypt(self.__encrypted_msgs[i]))
