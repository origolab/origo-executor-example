class DataUtils:
    @staticmethod
    def bits2str(bits):
        """
        Convert bits to string. from https://stackoverflow.com/questions/9916334/bits-to-string-python
        Args:
            bits: input bits string.
        Returns:
            string, the converted string from bits.
        """
        return ''.join(chr(int(''.join(x), 2)) for x in zip(*[iter(bits)] * 8))

    @staticmethod
    def int2bytestr(integer, num_of_bits):
        """
        Convert integer to the byte-wise string interpretation.
        Args:
            integer: input integer.

        Returns:
            string, the converted string.

        """
        format_string = '{0:0' + str(num_of_bits) + 'b}'
        return DataUtils.bits2str(format_string.format(integer))

    @staticmethod
    def int2bytes(integer, num_of_bytes):
        """
        Convert integer to the byte-wise string interpretation.
        Args:
            integer: input integer.

        Returns:
            bytes[], the converted byte arrary.

        """
        format_string = '{0:0' + str(num_of_bytes * 8) + 'b}'
        bin_str = format_string.format(integer)
        values = []
        for i in range(num_of_bytes):
            values.append(int(bin_str[i * 8: (i + 1) * 8], 2))
        return bytes(values)

    @staticmethod
    def bytestr2int(byte_str):
        """
        Conver the byte str "\x00\x00...." style to integer.
        Args:
            byte_str: byte string.

        Returns:
            int, the converted integer.

        """
        return int.from_bytes(byte_str.encode(), byteorder='big')

    @staticmethod
    def bytes2int(bytes):
        """
        Conver the byte str "\x00\x00...." style to integer.
        Args:
            bytes: bytes.

        Returns:
            int, the converted integer.

        """
        return int.from_bytes(bytes, byteorder='big')

    @staticmethod
    def concatenate_split_data(data_array, data_bit_width):
        """
        Concatenate the split data into one single int.
        Args:
            data_array: [int], the split bits (represented as integer)
            data_bit_width: int, the bit length of each data.

        Returns:
            int, a single concatenated integer.

        """
        ret_bin_str = ''
        format_str = '{0:0' + str(data_bit_width) + 'b}'
        for data in data_array:
            ret_bin_str += format_str.format(data)
        return int(ret_bin_str, 2)
