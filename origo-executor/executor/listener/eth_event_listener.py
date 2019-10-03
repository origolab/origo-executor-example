from executor.listener.event_listener import EventListener
from executor.chain_interface.eth_localabi_interface import EthLocalABIInterface
from executor.utils.log_utils import LogUtils
from executor.zokrates_utils.zokrates_eth_file_downloader import ZokratesEthFileDownloader
from executor.zokrates_utils.zokrates_code_compiler import ZokratesCodeCompiler


class EthEventListener(EventListener):
    """
    The EventListener for ETH.
    """
    def __init__(self, executor, listener_config, event_queue, debug=False):
        """
        Init the EthEventListener.
        Args:
            executor: the owner Executor.
            listener_config: dictionary, the listener configuration.
            event_queue: Queue, the queue for putting event and commitment in.
            debug: boolean, debug flag.
        """
        EventListener.__init__(self, executor, listener_config, event_queue, debug)
        self.__downloader = ZokratesEthFileDownloader(self.chain_interface)

    def create_chain_interface(self, chain_config):
        """
        Create the block chain interface based on the given configuration.
        Args:
            chain_config: dictionary. The chain configuration.

        Returns:
            ChainInterface.

        """
        return EthLocalABIInterface(chain_config)

    def setup(self, executor):
        """
        The setup function before the thread starts to wait for the event arriving.
        Args:
            executor: the owner Executor.

        """
        # Update the single commitment size info first.
        secs = self.chain_interface.get_single_execution_commitment_size(self.contract_address)
        executor.update_contract_info(self.contract_address, 'single_execution_commitment_size', secs)

        # For current Zokrates based executor, we need to download the required files before listening started.
        assert 'proving_key_path' in self.config
        assert 'code_path' in self.config
        assert 'abi_path' in self.config
        destination_paths = {'proving_key_path': self.config['proving_key_path'],
                             'code_path': self.config['code_path'],
                             'abi_path': self.config['abi_path']}
        if self.debug:
            LogUtils.info("Start to download required files")
        self.__downloader.download_required_files(self.contract_address, destination_paths,
                                                  self.config['use_existing_data'])
        if self.debug:
            LogUtils.info("Start to compile required Zokrates code")
        assert 'zokrates_path' in self.config
        ZokratesCodeCompiler.compile_code(self.contract_address, self.config['zokrates_path'],
                                          self.config['code_path'], self.config['working_path'])
