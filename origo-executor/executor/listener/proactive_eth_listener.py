from executor.listener.eth_event_listener import EthEventListener
from executor.utils.log_utils import LogUtils
from executor.zokrates_utils.zokrates_eth_file_downloader import ZokratesEthFileDownloader
from gevent import sleep
from web3.exceptions import BadFunctionCallOutput


class ProactiveEthListener(EthEventListener):
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
        EthEventListener.__init__(self, executor, listener_config, event_queue, debug)
        self.__downloader = ZokratesEthFileDownloader(self.chain_interface)

    def wait_for_commitment_open(self, poll_interval, callback):
        """
        The listening function, which will wait and notified until the commitment opening event of the target contract.
        then invoke the provided callback function.
        Args:
            poll_interval: int, The interval between each check.
            callback: function, the function invoked after each event received.

        """
        try:
            if self.chain_interface.check_is_open_finished(self.contract_address):
                commitments = self.chain_interface.get_input_and_commitment(self.contract_address)
                event_info = {'contract_address': self.contract_address, 'commitments': commitments}
                self.queue.put(event_info)
                self.stop()
            sleep(1)
        except BadFunctionCallOutput as e:
            LogUtils.warning('BadFunctionCallOutput:' + str(e) + '\nContinue listening...')

