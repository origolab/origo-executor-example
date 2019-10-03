class EthInterfaceConstants:
    """
    Class for holding the constants used by EthInterface.
    """
    DEFAULT_CALL_GAS = 6000000
    DEFAULT_CALL_GAS_PRICE = 1
    VERIFY_AND_SETTLE_GAS = 6000000

    DEFAULT_ABI = [
        {'constant': True, 'inputs': [], 'name': 'getProvingKeyPath', 'outputs': [{'name': '', 'type': 'string'}],
         'payable': False, 'stateMutability': 'view', 'type': 'function'},
        {'constant': True, 'inputs': [], 'name': 'getVariablesPath', 'outputs': [{'name': '', 'type': 'string'}],
         'payable': False, 'stateMutability': 'view', 'type': 'function'},
        {'constant': True, 'inputs': [], 'name': 'getCodePath', 'outputs': [{'name': '', 'type': 'string'}],
         'payable': False, 'stateMutability': 'view', 'type': 'function'},
        {'constant': True, 'inputs': [], 'name': 'getAbiPath', 'outputs': [{'name': '', 'type': 'string'}],
         'payable': False, 'stateMutability': 'view', 'type': 'function'},
        {'constant': True, 'inputs': [], 'name': 'getProvingKeySha2', 'outputs': [{'name': '', 'type': 'uint256'}],
         'payable': False, 'stateMutability': 'view', 'type': 'function'},
        {'constant': True, 'inputs': [], 'name': 'getCodeSha2', 'outputs': [{'name': '', 'type': 'uint256'}],
         'payable': False, 'stateMutability': 'view', 'type': 'function'},
        {'constant': True, 'inputs': [], 'name': 'getVariablesSha2', 'outputs': [{'name': '', 'type': 'uint256'}],
         'payable': False, 'stateMutability': 'view', 'type': 'function'},
        {'constant': True, 'inputs': [], 'name': 'getAbiSha2', 'outputs': [{'name': '', 'type': 'uint256'}],
         'payable': False, 'stateMutability': 'view', 'type': 'function'},
        {'constant': True, 'inputs': [], 'name': 'isOpenFinished', 'outputs': [{'name': '', 'type': 'bool'}],
         'payable': False, 'stateMutability': 'view', 'type': 'function'},
        {'constant': True, 'inputs': [], 'name': 'getInputAndCommitment',
         'outputs': [{'name': '', 'type': 'uint256[]'}], 'payable': False, 'stateMutability': 'view',
         'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'getSingleExecutionCommitmentSize',
                               'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False,
                               'stateMutability': 'view', 'type': 'function'}]
