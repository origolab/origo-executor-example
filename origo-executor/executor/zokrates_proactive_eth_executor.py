from executor.zokrates_eth_executor import ZokratesEthExecutor
from executor.listener.proactive_eth_listener import ProactiveEthListener
from executor.utils.log_utils import LogUtils


class ZokratesProactiveEthExecutor(ZokratesEthExecutor):
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
        ZokratesEthExecutor.__init__(self, executor_options, debug)

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
        return ProactiveEthListener(self, listener_config, event_queue, self.debug)
