from abc import ABC
from abc import abstractmethod


class ChainInterface(ABC):
    """
    The base class for the block chain interface, which defines the way of interacting between Executor and the chain.
    """
    @abstractmethod
    def wait_for_commitment_open(self, contract_address, callback, owner, from_block='latest', to_block='latest',
                                 poll_interval=2):
        """,
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
        raise NotImplementedError('Abstract method, not implemented yet')

    @abstractmethod
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
        raise NotImplementedError('Abstract method, not implemented yet')

    @abstractmethod
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
        raise NotImplementedError('Abstract method, not implemented yet')