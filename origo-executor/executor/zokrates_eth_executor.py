from executor.executor import Executor
from executor.worker.zokrates_eth_worker import ZokratesEthWorker
from executor.listener.eth_event_listener import EthEventListener
from executor.utils.log_utils import LogUtils
from os import path, remove


class ZokratesEthExecutor(Executor):
    """
    File based executor, i.e. some of the steps among contract execution, proof generation and so on depend on data
    on the file system.
    """
    def __init__(self, executor_options, debug=False):
        """
        Init file based Executor.
        Args:
            executor_options: dictionary, for configuration usage.
            debug: boolean, whether enable debug mode.
        """
        Executor.__init__(self, executor_options, debug)
        # File path for proving key and contract code.
        self.__proving_key_path = executor_options['proving_key_path']
        self.__abi_path = executor_options['abi_path']
        self.__code_path = executor_options['code_path']
        self.__working_folder_path = executor_options['working_path']
        self.__zokrates_path = executor_options['zokrates_path']
        self.__chain_config = executor_options['chain_config']

    @staticmethod
    def check_options(options):
        """
        Check the input options are valid.
        Args:
            options: options: dictionary, for configuration usage.
        """
        if 'proving_key_path' not in options:
            raise Exception("Executor cannot find proving key path in configuration.")
        if 'code_path' not in options:
            raise Exception("Executor cannot find contract path in configuration.")
        if 'working_path' not in options:
            raise Exception("Executor cannot find working path in configuration.")
        if "zokrates_path" not in options:
            raise Exception("Executor cannot find zokrates path in configuration.")
        if "chain_config" not in options:
            raise Exception("Executor cannot find chain option in configuration")
        if "use_existing_data" not in options:
            raise Exception("Executor cannot find use_existing_data setting in configuration")

    def create_worker(self, contract_address, execution_id, commitments, execution_queue):
        """
        Create the worker thread for the given execution.
        Args:
            contract_address: string, contract address.
            execution_id: int, the execution id for unique execution of this contract.
            commitments: commitments released by the given contract.
            execution_queue: the queue for storing the execution result from workers.

        Returns:
            ExecutionWorker. The worker for the given execution.

        """
        execution_info = {'contract_address': contract_address,
                          'execution_id': execution_id,
                          'zokrates_path': self.__zokrates_path,
                          'commitments': commitments,
                          'proving_key_path': self.__proving_key_path,
                          'code_path': self.__code_path,
                          'working_path': self.__working_folder_path,
                          'encryption_info': self.options['encryption_info']}

        if self.debug:
            LogUtils.info("Enable debug mode for worker!")

        return ZokratesEthWorker(execution_info, self.__chain_config, execution_queue, self.submit_lock, self.debug)

    def create_listener(self, listener_config, event_queue):
        """
        Create the EventListener for the given contract address.
        Args:
            listener_config: dictionary, the configuration of listener.
            event_queue: Queue.

        Returns:
            EventListener thread.

        """
        if self.debug:
            LogUtils.info("Enable debug mode for listener!")
        return EthEventListener(self, listener_config, event_queue, self.debug)

    def unregister_clean_up(self, contract_address):
        """
        Do the post-clean up after unregistered any registered contracts.
        Args:
            contract_address: string, contract address.

        """
        abi_path = path.join(self.__abi_path, contract_address) + '.abi'
        proving_key_path = path.join(self.__proving_key_path, contract_address) + '.pk'
        variables_path = path.join(self.__proving_key_path, contract_address) + '.var'
        code_path = path.join(self.__code_path, contract_address) + '.code'
        compiled_code_path = path.join(self.__working_folder_path, 'compiled_code', contract_address) + '_out'

        if path.isfile(abi_path):
            remove(abi_path)

        if path.isfile(proving_key_path):
            remove(proving_key_path)

        if path.isfile(variables_path):
            remove(variables_path)

        if path.isfile(code_path):
            remove(code_path)

        if path.isfile(compiled_code_path):
            remove(compiled_code_path)
