from executor.chain_interface.chain_interface import ChainInterface
from executor.constants.eth_interface_constants import EthInterfaceConstants
from gevent import sleep
from web3 import Web3


class EthInterface(ChainInterface):
    """
    The ETH block chain interface.
    """
    def __init__(self, options):
        """
        Init the ETH block chain interface.
        Args:
            options: dictionary, all the required information for initializing the interface.
        """
        self.__provider = None
        assert 'provider_type' in options
        provider_type = options['provider_type']
        if provider_type == 'ipc':
            assert 'ipc_path' in options
            self.__provider = Web3.IPCProvider(options['ipc_path'])
        elif provider_type == 'http':
            assert 'http_uri' in options
            self.__provider = Web3.HTTPProvider(options['http_uri'])
        elif provider_type == 'websocket':
            assert 'websocket_uri' in options
            self.__provider = Web3.WebsocketProvider(options['websocket_uri'])

        # The provider must not None
        assert self.__provider is not None

        # Check the web3 interface is Connected
        self.__web3 = Web3(self.__provider)
        assert self.__web3.isConnected()

        self.__default_abi = self._load_default_abi()

        assert 'default_account' in options
        self.__default_account = options['default_account']
        self.__web3.eth.defaultAccount = options['default_account']

        self.__private_key = None
        self.__public_key = None
        if 'private_key' in options and options['private_key'] != '' and \
           'public_key' in options and options['public_key'] != '':
            self.__private_key = options['private_key']
            self.__public_key = options['public_key']

    def _load_default_abi(self, abi_path=None):
        """
        Load the default abi, which is used to invoke the fixed API for all supported contracts.
        Args:
            abi_path: the path to load the default abi.
        Returns:
            Default abi.

        """
        return EthInterfaceConstants.DEFAULT_ABI

    @staticmethod
    def event_listen_loop(event_filter, callback, poll_interval, owner):
        """
        The event listening loop.
        Args:
            event_filter: eventFilter, the target event to listen on.
            callback: function, the callback function for listened event.
            poll_interval: int, the poll interval.
            owner: the owner listener thread of this interface. Which should be live to keep this waiting function
                work.

        """
        while not owner.should_exit():
            for event in event_filter.get_new_entries():
                callback(event)
            sleep(poll_interval)

    @staticmethod
    def event_listen_loop_for_result(event_filter, execution_id, callback, poll_interval, owner):
        """
        The event listening loop.
        Args:
            event_filter: eventFilter, the target event to listen on.
            execution_id: int, the identity number for different execution of the same contract.
            callback: function, the callback function for listened event.
            poll_interval: int, the poll interval.
            owner: the owner listener thread of this interface. Which should be live to keep this waiting function
                work.

        """
        while not owner.should_exit():
            for event in event_filter.get_new_entries():
                if event.args.execution_id == execution_id:
                    callback(event)
                    return
            sleep(poll_interval)

    def wait_for_commitment_open(self, contract_address, callback, owner, from_block='latest', to_block='latest',
                                 poll_interval=2):
        """
        The listening function, which will wait and notified until the commitment opening event of the target contract.
        then invoke the provided callback function. Or return without invoking after the timeout.
        Args:
            contract_address: string, the address or id of the target contract.
            callback: function, the callback function after the commitment open event notifies.
            owner: the owner listener thread of this interface. Which should be live to keep this waiting function
                work.
            from_block: starting block (exclusive) filter block range. It can be either the starting block number, or
                ‘latest’ for the last mined block, or ‘pending’ for unmined transactions.
            to_block: ending block (exclusive) filter block range. It can be either the starting block number, or
                ‘latest’ for the last mined block, or ‘pending’ for unmined transactions.
            poll_interval: int, the interval of polling event.

        """
        contract_abi = self.get_abi_for_contract(contract_address)
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        event_filter = target_contract.eventFilter('CommitmentOpen', {'fromBlock': from_block, 'toBlock': to_block})
        self.event_listen_loop(event_filter, callback, poll_interval, owner)

    def wait_for_verify_and_settle_event(self, contract_address, execution_id, callback, owner, from_block='latest',
                                         to_block='latest', poll_interval=2):
        """
        The listening function, which will wait and notified until the verifyAndSettle event of the target contract.
        then invoke the provided callback function. Or return without invoking after the timeout defined by the owner.
        Args:
            contract_address: string, the address or id of the target contract.
            execution_id: int, the identity number for different execution of the same contract.
            callback: function, the callback function after the commitment open event notifies.
            owner: the owner worker thread of this interface. Which should be live to keep this waiting function
                work.
            from_block: starting block (exclusive) filter block range. It can be either the starting block number, or
                ‘latest’ for the last mined block, or ‘pending’ for unmined transactions.
            to_block: ending block (exclusive) filter block range. It can be either the starting block number, or
                ‘latest’ for the last mined block, or ‘pending’ for unmined transactions.
            poll_interval: int, the interval of polling event.

        """
        self.event_listen_loop_for_result(contract_address, execution_id, callback, poll_interval, owner)

    @staticmethod
    def hex_array_to_int_array(arr):
        return list(map(lambda x: int(x, 0), arr))

    def invoke_verify_and_settle(self, contract_address, execution_id, verification_data):
        """
        Invoke the "verifyAndSettle" function of the target contract with the verification data.
        Args:
            contract_address: string, the address or id of the target contract.
            execution_id: int, the identity number for different execution of the same contract.
            verification_data: dictionary, the data required for the online verification.

        Returns:
            The transaction hash of the invoked "verifyAndSettle" function.

        """
        contract_abi = self.get_abi_for_contract(contract_address)
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        if self.__private_key is None or self.__public_key is None:
            tx_hash = target_contract.functions.verifyAndSettle(
                execution_id,
                self.hex_array_to_int_array(verification_data['A']),
                self.hex_array_to_int_array(verification_data['A_p']),
                list(map(lambda x: self.hex_array_to_int_array(x), verification_data['B'])),
                self.hex_array_to_int_array(verification_data['B_p']),
                self.hex_array_to_int_array(verification_data['C']),
                self.hex_array_to_int_array(verification_data['C_p']),
                self.hex_array_to_int_array(verification_data['H']),
                self.hex_array_to_int_array(verification_data['K']),
                verification_data['inputs']).transact({'gas': EthInterfaceConstants.VERIFY_AND_SETTLE_GAS})
        else:
            nonce = self.__web3.eth.getTransactionCount(self.__public_key)
            vs_txn = target_contract.functions.verifyAndSettle(
                execution_id,
                self.hex_array_to_int_array(verification_data['A']),
                self.hex_array_to_int_array(verification_data['A_p']),
                list(map(lambda x: self.hex_array_to_int_array(x), verification_data['B'])),
                self.hex_array_to_int_array(verification_data['B_p']),
                self.hex_array_to_int_array(verification_data['C']),
                self.hex_array_to_int_array(verification_data['C_p']),
                self.hex_array_to_int_array(verification_data['H']),
                self.hex_array_to_int_array(verification_data['K']),
                verification_data['inputs']).\
                buildTransaction({
                    'chainId': 27,
                    'gas': EthInterfaceConstants.VERIFY_AND_SETTLE_GAS,
                    'gasPrice': self.__web3.toWei('1', 'gwei'),
                    'nonce': nonce})
            signed_txn = self.__web3.eth.account.signTransaction(vs_txn, private_key=self.__private_key)
            tx_hash = self.__web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        self.__web3.eth.waitForTransactionReceipt(tx_hash)

    def init_verify_and_settle_event_listener(self, contract_address):
        """
        Init the VerifyAndSettle Event handler before the event emit.
        Args:
            contract_address: contract address

        Returns:
            The EventFilter for the VerifyAndSettle event.

        """
        contract_abi = self.get_abi_for_contract(contract_address)
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        return target_contract.events.VerifyAndSettle.createFilter(fromBlock='latest')
        # return target_contract.eventFilter('VerifyAndSettle', {'fromBlock': 'latest', 'toBlock': 'latest'})

    def get_abi_for_contract(self, contract_address):
        """
        Get the abi for the target contract.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            The abi for the target contract or None if failed to get the abi.

        """
        raise NotImplementedError('Abstract method, not implemented yet')

    def get_default_abi(self):
        """
        Get the default Abi, which is used to invoke the fixed API for all supported contracts.
        Returns:
            Default abi.

        """
        return self.__default_abi

    def get_abi_file_path(self, contract_address):
        """
        Get the path to download abi file for target contract.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            string, the http uri to download the abi file.

        """
        contract_abi = self.get_default_abi()
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        return target_contract.functions.getAbiPath().call({
            'from': self.__default_account,
            'gas': EthInterfaceConstants.DEFAULT_CALL_GAS,
            'gasPrice': EthInterfaceConstants.DEFAULT_CALL_GAS_PRICE
        })

    def get_code_file_path(self, contract_address):
        """
        Get the path to download code file for target contract.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            string, the http uri to download the code file.

        """
        contract_abi = self.get_default_abi()
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        return target_contract.functions.getCodePath().call({
            'from': self.__default_account,
            'gas': EthInterfaceConstants.DEFAULT_CALL_GAS,
            'gasPrice': EthInterfaceConstants.DEFAULT_CALL_GAS_PRICE
        })

    def get_proving_key_path(self, contract_address):
        """
        Get the path to download code file for target contract.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            string, the http uri to download the code file.

        """
        contract_abi = self.get_default_abi()
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        return target_contract.functions.getProvingKeyPath().call({
            'from': self.__default_account,
            'gas': EthInterfaceConstants.DEFAULT_CALL_GAS,
            'gasPrice': EthInterfaceConstants.DEFAULT_CALL_GAS_PRICE
        })

    def get_variables_file_path(self, contract_address):
        """
        Get the path to download variables file for target contract.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            string, the http uri to download the variables file.

        """
        contract_abi = self.get_default_abi()
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        return target_contract.functions.getVariablesPath().call({
            'from': self.__default_account,
            'gas': EthInterfaceConstants.DEFAULT_CALL_GAS,
            'gasPrice': EthInterfaceConstants.DEFAULT_CALL_GAS_PRICE
        })

    def get_abi_hash(self, contract_address):
        """
        Get the hash value of the abi file.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            int, the hash value.

        """
        contract_abi = self.get_default_abi()
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        return target_contract.functions.getAbiSha2().call({
            'from': self.__default_account,
            'gas': EthInterfaceConstants.DEFAULT_CALL_GAS,
            'gasPrice': EthInterfaceConstants.DEFAULT_CALL_GAS_PRICE
        })

    def get_proving_key_hash(self, contract_address):
        """
        Get the hash value of the proving key file.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            int, the hash value.

        """
        contract_abi = self.get_default_abi()
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        return target_contract.functions.getProvingKeySha2().call({
            'from': self.__default_account,
            'gas': EthInterfaceConstants.DEFAULT_CALL_GAS,
            'gasPrice': EthInterfaceConstants.DEFAULT_CALL_GAS_PRICE
        })

    def get_variables_hash(self, contract_address):
        """
        Get the hash value of the variables.inf file.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            int, the hash value.

        """
        contract_abi = self.get_default_abi()
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        return target_contract.functions.getVariablesSha2().call({
            'from': self.__default_account,
            'gas': EthInterfaceConstants.DEFAULT_CALL_GAS,
            'gasPrice': EthInterfaceConstants.DEFAULT_CALL_GAS_PRICE
        })

    def get_code_hash(self, contract_address):
        """
        Get the hash value of the code file.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            int, the hash value.

        """
        contract_abi = self.get_default_abi()
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        return target_contract.functions.getCodeSha2().call({
            'from': self.__default_account,
            'gas': EthInterfaceConstants.DEFAULT_CALL_GAS,
            'gasPrice': EthInterfaceConstants.DEFAULT_CALL_GAS_PRICE
        })

    def check_is_open_finished(self, contract_address):
        """
        Check whether IsOpenFinished function return true.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            boolean.

        """
        contract_abi = self.get_default_abi()
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        return target_contract.functions.isOpenFinished().call({
            'from': self.__default_account,
            'gas': EthInterfaceConstants.DEFAULT_CALL_GAS,
            'gasPrice': EthInterfaceConstants.DEFAULT_CALL_GAS_PRICE
        })

    def get_input_and_commitment(self, contract_address):
        """
        Invoke the getInputAndCommitment function of target contract.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            the commitment list from contract.

        """
        contract_abi = self.get_default_abi()
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        commitment = target_contract.functions.getInputAndCommitment().call({
            'from': self.__default_account,
            'gas': EthInterfaceConstants.DEFAULT_CALL_GAS,
            'gasPrice': EthInterfaceConstants.DEFAULT_CALL_GAS_PRICE
        })
        return commitment

    def get_single_execution_commitment_size(self, contract_address):
        """
        Invoke the getSingleExecutionCommitmentSize function of target contract.
        Args:
            contract_address: string, the address or id of the target contract.

        Returns:
            the commitment list from contract.

        """
        contract_abi = self.get_default_abi()
        assert contract_abi is not None
        target_contract = self.__web3.eth.contract(address=contract_address, abi=contract_abi)
        target_contract.address = contract_address
        size = target_contract.functions.getSingleExecutionCommitmentSize().call({
            'from': self.__default_account,
            'gas': EthInterfaceConstants.DEFAULT_CALL_GAS,
            'gasPrice': EthInterfaceConstants.DEFAULT_CALL_GAS_PRICE
        })
        return size
