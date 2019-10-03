import hashlib
import urllib.request

from executor.listener.event_listener_exception import FileDownloadException, CheckSumException
from executor.utils.file_utils import FileUtils
from os import path
from urllib.error import URLError


class ZokratesEthFileDownloader:
    """
    The file downloader which can download the required files of Zokrates from contracts.
    """
    def __init__(self, eth_interface):
        """
        Init the ZokratesEthFileDownloader.
        Args:
            eth_interface: EthInterface, the interface to interact with block chain.
        """
        self.__eth_interface = eth_interface

    @staticmethod
    def file_checksum(file_path, hash_value):
        """
        Check the file's hash matches the expected value.
        Args:
            file_path: string, file_path
            hash_value: int, expected hash_value.

        Returns:
            Boolean, return True if matches the hash, otherwise return False.

        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        computed_hash = int(sha256_hash.hexdigest(), 16)
        return computed_hash == hash_value

    def download_required_files(self, contract_address, destination_paths, use_existing_data):
        """
        Download the required files to the destination paths.
        Args:
            contract_address: string, contract_address
            destination_paths: dictionary, the destination paths.
            use_existing_data: boolean, whether skipping downloading if local data already exists.

        Returns:
            Boolean, whether the required files are all downloaded successfully.

        """
        assert 'proving_key_path' in destination_paths
        assert 'code_path' in destination_paths
        assert 'abi_path' in destination_paths
        local_proving_key_path = destination_paths['proving_key_path']
        local_code_path = destination_paths['code_path']
        local_abi_path = destination_paths['abi_path']
        FileUtils.create_folders([local_proving_key_path, local_code_path, local_abi_path])

        abi_destination = path.join(local_abi_path, contract_address) + '.abi'
        proving_key_destination = path.join(local_proving_key_path, contract_address) + '.pk'
        variables_destination = path.join(local_proving_key_path, contract_address) + '.var'
        code_destination = path.join(local_code_path, contract_address) + '.code'

        if not use_existing_data or not FileUtils.files_exisit([abi_destination]):
            abi_download_path = self.__eth_interface.get_abi_file_path(contract_address)
            try:
                urllib.request.urlretrieve(abi_download_path, abi_destination)
            except urllib.error.URLError:
                raise FileDownloadException
        if not use_existing_data or not FileUtils.files_exisit([proving_key_destination]):
            proving_key_download_path = self.__eth_interface.get_proving_key_path(contract_address)
            try:
                urllib.request.urlretrieve(proving_key_download_path, proving_key_destination)
            except urllib.error.URLError:
                raise FileDownloadException
        if not use_existing_data or not FileUtils.files_exisit([variables_destination]):
            variables_download_path = self.__eth_interface.get_variables_file_path(contract_address)
            try:
                urllib.request.urlretrieve(variables_download_path, variables_destination)
            except urllib.error.URLError:
                raise FileDownloadException
        if not use_existing_data or not FileUtils.files_exisit([code_destination]):
            code_download_path = self.__eth_interface.get_code_file_path(contract_address)
            try:
                urllib.request.urlretrieve(code_download_path, code_destination)
            except urllib.error.URLError:
                raise FileDownloadException

        abi_hash = self.__eth_interface.get_abi_hash(contract_address)
        if not self.file_checksum(abi_destination, abi_hash):
            raise CheckSumException("abi file failed checksum.")

        code_hash = self.__eth_interface.get_code_hash(contract_address)
        if not self.file_checksum(code_destination, code_hash):
            raise CheckSumException("code file failed checksum.")

        proving_key_hash = self.__eth_interface.get_proving_key_hash(contract_address)
        if not self.file_checksum(proving_key_destination, proving_key_hash):
            raise CheckSumException("proving key file failed checksum.")

        variables_hash = self.__eth_interface.get_variables_hash(contract_address)
        if not self.file_checksum(variables_destination, variables_hash):
            raise CheckSumException("variables file failed checksum.")
