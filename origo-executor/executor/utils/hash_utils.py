import hashlib

from executor.utils.data_utils import DataUtils


class HashUtils:
    @staticmethod
    def compute_sha256(commitment, num_of_bits):
        """
        Computethe sha256 of the given commitment.
        Args:
            commitment: int, the input integer.
            num_of_bits: the number of bits to convert to.

        Returns:
            sha256 hash value.

        """
        format_str = "{0:0" + str(num_of_bits) + "b}"
        bits_str = format_str.format(commitment)
        return int(hashlib.sha256(DataUtils.bits2str(bits_str).encode('raw_unicode_escape')).hexdigest(), 16)

    @staticmethod
    def compute_sha256_for_bitstr(bits_str):
        """
        Computethe sha256 of the given commitment.
        Args:
            bits_str: string, "010101" format string.

        Returns:
            sha256 hash value.

        """
        return int(hashlib.sha256(DataUtils.bits2str(bits_str).encode('raw_unicode_escape')).hexdigest(), 16)
