from abc import abstractmethod
from executor.listener.event_listener_exception import SetupException
from executor.listener.event_listener_status import EventListenerStatus
from executor.utils.log_utils import LogUtils
from web3.exceptions import InvalidAddress
from gevent import Greenlet


class EventListener(Greenlet):
    """
    The thread to listen certain contract's event.
    """
    def __init__(self, executor, listener_config, event_queue, debug=False):
        """
        Init EventListener.
        Args:
            executor: the owner Executor.
            listener_config: dictionary, the listener configuration.
            event_queue: Queue, the queue for putting event and commitment in.
            debug: boolean, debug flag.
        """
        Greenlet.__init__(self)
        self.__should_exit = False
        self.__executor = executor
        self.queue = event_queue
        self.debug = debug

        assert 'contract_address' in listener_config
        self.contract_address = listener_config['contract_address']
        assert 'poll_interval' in listener_config
        self.__poll_interval = listener_config['poll_interval']

        assert 'chain_config' in listener_config
        self.chain_interface = self.create_chain_interface(listener_config['chain_config'])

        self.config = listener_config

    @abstractmethod
    def create_chain_interface(self, chain_config):
        """
        Create the block chain interface based on the given configuration.
        Args:
            chain_config: dictionary. The chain configuration.

        Returns:
            ChainInterface.

        """
        raise NotImplementedError('Abstract method, not implemented yet')

    def _put_event_into_queue(self, event):
        """
        This is the callback of the commitment open event. It puts the event info into the event queue.
        Args:
            event: The received event.

        """
        event_info = {'contract_address': self.contract_address, 'commitments': event.args.commitments}
        self.queue.put(event_info)

    def wait_for_commitment_open(self, poll_interval, callback):
        """
        The listening function, which will wait and notified until the commitment opening event of the target contract.
        then invoke the provided callback function.
        Args:
            poll_interval: int, The interval between each check.
            callback: function, the function invoked after each event received.

        """
        self.chain_interface.wait_for_commitment_open(
            self.contract_address, callback, self)

    @abstractmethod
    def setup(self, executor):
        """
        The setup function before the thread starts to wait for the event arriving.
        Args:
            executor: the owner Executor.

        """
        raise NotImplementedError('Abstract method, not implemented yet')

    def _run(self):
        # Before start to wait, can do some setup, like file downloading...
        if self.debug:
            LogUtils.info("Start setup before listening.")
        try:
            self.setup(self.__executor)
        except InvalidAddress as e:
            if self.debug:
                LogUtils.info("Setup failed: " + str(e))
            event_info = {'contract_address': self.contract_address, 'status': EventListenerStatus.SETUP_FAILED,
                          'debug_msg': str(e)}
            self.queue.put(event_info)
            return
        except SetupException as e:
            if self.debug:
                LogUtils.info("Setup failed: " + str(e))
            event_info = {'contract_address': self.contract_address, 'status': EventListenerStatus.SETUP_FAILED,
                          'debug_msg': str(e)}
            self.queue.put(event_info)
            return
        event_info = {'contract_address': self.contract_address, 'status': EventListenerStatus.SETUP_SUCCEEDED}
        self.queue.put(event_info)
        if self.debug:
            LogUtils.info("Setup finished, start to listening on CommitmentOpen")
        while not self.__should_exit:
            self.wait_for_commitment_open(self.__poll_interval, self._put_event_into_queue)

    def stop(self):
        """
        Stop this listener thread.

        """
        self.__should_exit = True

    def should_exit(self):
        """
        Return the thread status.
        Returns:
            boolean, whether the thread should stop or not.
        """
        return self.__should_exit
