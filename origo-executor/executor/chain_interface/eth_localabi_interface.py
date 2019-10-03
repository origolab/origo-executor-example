from executor.chain_interface.eth_interface import EthInterface
from os import path

import json


class EthLocalABIInterface(EthInterface):
    """
    The ETH interface with local stored contract Abi files.
    """
    def __init__(self, options):
        """
        Init the ETH block chain interface.
        Args:
            options: dictionary, all the required information for initializing the interface.
        """
        EthInterface.__init__(self, options)

        assert 'abi_path' in options
        self.__abi_path = options['abi_path']

    def get_abi_for_contract(self, contract_address):
        """
        Get the abi for the target contract.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            The abi for the target contract or None if failed to get the abi.

        """
        abi_file_path = path.join(self.__abi_path, contract_address) + '.abi'
        with open(abi_file_path) as f:
            return json.load(f)
