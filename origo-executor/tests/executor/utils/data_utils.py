import unittest

from executor.utils.data_utils import DataUtils


class EthInterfaceTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_bits2str(self):
        # test static method bits2str
        self.assertEqual('\x05',
                         DataUtils.bits2str('00000101'))

    def test_int2bytstr(self):
        # test static method int2bytstr
        self.assertEqual('\x05',
                         DataUtils.int2bytestr(5, 8))

        self.assertEqual('\x00\x05',
                         DataUtils.int2bytestr(5, 16))

    def test_bytestr2int(self):
        self.assertEqual(5,
                         DataUtils.bytestr2int(DataUtils.int2bytestr(5, 8)))

        self.assertEqual(11110,
                         DataUtils.bytestr2int(DataUtils.int2bytestr(11110, 512)))