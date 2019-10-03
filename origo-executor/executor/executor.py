import threading
import time

from abc import abstractmethod, abstractstaticmethod
from executor.constants.executor_constants import ExecutorConstants
from executor.listener.event_listener_status import EventListenerStatus
from executor.worker.execution_result import ExecutionResult
from executor.utils.log_utils import LogUtils
from gevent.lock import Semaphore
from queue import Queue


class TaskStatus:
    """
    The task status maintained by the executor.
    """
    REGISTERING, FAILED_TO_REGISTER, LISTENING, EXECUTING, FINISHED, UNREGISTERING, UNREGISTERED = range(7)

    @staticmethod
    def get_status_info(status):
        """
        Get the status info string.
        Args:
            status: TaskStatus.

        Returns:
            string, the status description string.

        """
        if status == TaskStatus.REGISTERING:
            return "REGISTERING"
        elif status == TaskStatus.LISTENING:
            return "LISTENING"
        elif status == TaskStatus.EXECUTING:
            return "EXECUTING"
        elif status == TaskStatus.FINISHED:
            return "FINISHED"
        elif status == TaskStatus.UNREGISTERING:
            return "UNREGISTERING"
        elif status == TaskStatus.UNREGISTERED:
            return "UNREGISTERED"
        elif status == TaskStatus.FAILED_TO_REGISTER:
            return "FAILED_TO_REGISTER"


class Executor(threading.Thread):
    """
    Executor base class.
    """

    def __init__(self, options, debug=False):
        """
        Init the Executor.
        Args:
            options: dictionary, for configuration usage.
            debug: boolean, whether enable debug mode.
        """
        threading.Thread.__init__(self)
        assert 'chain_config' in options
        assert 'poll_interval' in options
        self.check_options(options)
        self.options = options
        self.should_exit = False
        self.debug = debug
        if self.debug:
            LogUtils.info("Enable debug mode for Executor!")

        # List of registered contracts.
        self.registered_contracts = {}
        # The latest execution id for the register contract.
        self.registered_contracts_execution_count = {}
        self.registered_contract_verification_failed_result_count = {}
        self.registered_contract_verification_result_count = {}
        # The pool of the execution worker threads.
        self.worker_pool = {}
        # The pool of the listener threads.
        self.listener_pool = {}
        self.execution_queue = Queue()
        self.event_queue = Queue()
        self.submit_lock = Semaphore()

        # The map of the status information for all the workers
        self.__task_status = {}

    def update_worker_status(self, contract_address, status, info=None):
        if status == TaskStatus.REGISTERING:
            if contract_address in self.__task_status and \
                    self.__task_status[contract_address]['status'] != TaskStatus.UNREGISTERED:
                LogUtils.error(
                    "Cannot register again registered contract@" + contract_address)
                return
        else:
            if contract_address not in self.__task_status:
                LogUtils.error(
                    "Cannot update status:" + TaskStatus.get_status_info(status) + " for not registered contract"
                    + '@' + contract_address)
                return

        if status == TaskStatus.REGISTERING:
            self.__task_status[contract_address] = {'status': status, 'finished_task': 0, 'successful_task': 0,
                                                    'progress': 0.0, 'failed_tasks': {}, 'info': ''}
        elif status == TaskStatus.LISTENING:
            self.__task_status[contract_address]['status'] = status
        elif status == TaskStatus.EXECUTING:
            assert self.__task_status[contract_address]['status'] in {TaskStatus.LISTENING, TaskStatus.EXECUTING}
            self.__task_status[contract_address]['status'] = status
            progress = \
                1.0 * self.registered_contract_verification_result_count[contract_address] / \
                self.registered_contracts_execution_count[contract_address]
            self.__task_status[contract_address]['progress'] = progress
            for failed_execution_id, info in \
                    self.registered_contract_verification_failed_result_count[contract_address].items():
                if failed_execution_id not in self.__task_status[contract_address]['failed_tasks']:
                    self.__task_status[contract_address]['failed_tasks'][failed_execution_id] = info
        elif status == TaskStatus.FINISHED:
            self.__task_status[contract_address]['finished_task'] += 1
            if not self.registered_contract_verification_failed_result_count[contract_address]:
                self.__task_status[contract_address]['successful_task'] += 1
            self.__task_status[contract_address]['progress'] = 0.0
            if contract_address in self.listener_pool and not self.listener_pool[contract_address].ready():
                # Go back to listening status if listener is still up after task is finished. but set the finished task
                # count incrementally.
                self.__task_status[contract_address]['status'] = TaskStatus.LISTENING
            else:
                self.__task_status[contract_address]['status'] = status
        elif status == TaskStatus.UNREGISTERING:
            self.__task_status[contract_address]['status'] = status
        elif status == TaskStatus.UNREGISTERED:
            self.__task_status[contract_address]['status'] = status
        elif status == TaskStatus.FAILED_TO_REGISTER:
            self.__task_status[contract_address]['status'] = status
            if info is not None:
                self.__task_status[contract_address]['info'] += (info + '; ')
        else:
            raise Exception("Unknown TaskStatus:" + str(status))

    def get_all_task_status(self):
        """
        Get the html element for task status.
        Returns:
            string, the html element for task status.

        """
        return self.__task_status

    @abstractstaticmethod
    def check_options(options):
        """
        Check the input options are valid.
        Args:
            options: options: dictionary, for configuration usage.
        """
        raise NotImplementedError('Abstract method, not implemented yet')

    def register_contract(self, contract_address, contract_info):
        """
        Register the contract which is supposed to be executed and proved with the Executor.
        Args:
            contract_address: contract address.
            contract_info: dictionary, the necessary contract info, may include (but not limited to)
                * contract code location to get
                * proving key location to get

        Returns:
            Boolean, if registration succeeded, return True, otherwise return False.
        """
        if contract_address in self.registered_contracts.keys():
            return False
        self.registered_contracts[contract_address] = contract_info
        self.registered_contracts_execution_count[contract_address] = 0
        self.registered_contract_verification_result_count[contract_address] = 0
        self.registered_contract_verification_failed_result_count[contract_address] = {}
        self.update_worker_status(contract_address, TaskStatus.REGISTERING)
        listener_config = {'contract_address': contract_address, 'poll_interval': self.options['poll_interval'],
                           'chain_config': self.options['chain_config'],
                           'proving_key_path': self.options['proving_key_path'],
                           'code_path': self.options['code_path'],
                           'abi_path': self.options['abi_path'],
                           'working_path': self.options['working_path'],
                           'zokrates_path': self.options['zokrates_path'],
                           'use_existing_data': self.options['use_existing_data']}
        listener = self.create_listener(listener_config, self.event_queue)
        self.listener_pool[contract_address] = listener
        # Listener starts here but it may still fail to listen, TaskStatus maybe FAILED_TO_REGISTER
        listener.start()
        return True

    def update_contract_info(self, contract_address, key, value):
        """
        Update the contract info for target contract address.
        Args:
            contract_address: string, contract address or id.
            key: string, contract info key.
            value: obj, contract info value.

        """
        if contract_address in self.registered_contracts:
            self.registered_contracts[contract_address][key] = value
        else:
            LogUtils.info("Cannot update non-registered contract info!")

    @abstractmethod
    def create_listener(self, listener_config, event_queue):
        """
        Create the EventListener for the given contract address.
        Args:
            listener_config: dictionary, the configuration of listener.
            event_queue: Queue. The event queue.

        Returns:
            EventListener thread.

        """
        raise NotImplementedError('Abstract method, not implemented yet')

    def unregister_clean_up(self, contract_address):
        """
        Do the post-clean up after unregistered any registered contracts.
        Args:
            contract_address: string, contract address.

        """
        pass

    def unregister_contract(self, contract_address):
        """
        Unregister the contract which is already registered with this Executor.
        Args:
            contract_address: contract address.

        Returns:
            Boolean, if succeeded, return True, otherwise return False.
        """
        if contract_address not in self.registered_contracts.keys():
            return False
        self.update_worker_status(contract_address, TaskStatus.UNREGISTERING)
        # Stop listeners
        assert contract_address in self.listener_pool
        if not self.listener_pool[contract_address].ready():
            self.listener_pool[contract_address].stop()
        self.listener_pool[contract_address].join()
        del self.listener_pool[contract_address]
        # Stop progressing workers if any
        if contract_address in self.worker_pool:
            self._clean_worker_pool(contract_address)
        del self.registered_contracts[contract_address]
        del self.registered_contracts_execution_count[contract_address]
        del self.registered_contract_verification_result_count[contract_address]
        del self.registered_contract_verification_failed_result_count[contract_address]
        self.unregister_clean_up(contract_address)
        self.update_worker_status(contract_address, TaskStatus.UNREGISTERED)
        if self.debug:
            LogUtils.info('Unregister contract@' + contract_address + ' succeeds')
        return True

    def handle_event_from_queue(self):
        """
        Get the event info and commitment from the event queue.

        Returns:
            contract address, string
            commitments, list
            status, EventListenerStatus
            debug_msg, string

        """
        event = self.event_queue.get()
        debug_msg = None
        if 'debug_msg' in event:
            debug_msg = event['debug_msg']
        assert 'contract_address' in event
        if 'commitments' in event:
            return event['contract_address'], event['commitments'], None, debug_msg
        elif 'status' in event:
            return event['contract_address'], None, event['status'], debug_msg
        else:
            raise Exception("Invalid event from listener:" + str(event))

    def get_execution_from_queue(self):
        """
        Get the execution result from queue.
        Returns:
            contract address and execution result.

        """
        event = self.execution_queue.get()
        assert 'contract_address' in event
        assert 'result' in event
        return event['contract_address'], event['result']

    @abstractmethod
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
        raise NotImplementedError('Abstract method, not implemented yet')

    def dispatch_worker(self, contract_address, execution_id, commitments):
        """
        Dispatch worker thread to do the execution and proof generation.
        Args:
            contract_address: string, contract address.
            execution_id: int, the execution id for unique execution of this contract.
            commitments: commitments released by the given contract.

        """
        if contract_address not in self.worker_pool.keys():
            self.worker_pool[contract_address] = {}
        if execution_id not in self.worker_pool[contract_address] or self.worker_pool[contract_address].ready():
            worker_thread = self.create_worker(contract_address, execution_id, commitments, self.execution_queue)
            self.worker_pool[contract_address][execution_id] = worker_thread
            worker_thread.start()
            if self.debug:
                LogUtils.info("Started the worker thread for contract@" + contract_address + " with execution_id: "
                              + str(execution_id))
        else:
            LogUtils.error("Cannot create more than one worker for the same contract and same execution id at the same"
                           "time.")

    def _get_single_execution_commitment_size(self, contract_address):
        """
        Get the required number of commitments for a single execution of the target contract.
        Args:
            contract_address: string, contract address or id.

        Returns:
            int, the required number of commitments.

        """
        if contract_address in self.registered_contracts:
            contract_info = self.registered_contracts[contract_address]
            if 'single_execution_commitment_size' in contract_info:
                return contract_info['single_execution_commitment_size']
        return None

    def run(self):
        """
        Listening on all the registered contracts' commitment opening event. If the event is triggered, then dispatch
        an ExecutorWorker thread to finish the proof.

        """
        while not self.should_exit:
            if not self.event_queue.empty():
                # Check the listener setup status first.
                contract_address, commitments, status, debug_msg = self.handle_event_from_queue()
                if status == EventListenerStatus.SETUP_SUCCEEDED:
                    if self.debug:
                        LogUtils.info("Status update for contract@" + contract_address + ": " +
                                      EventListenerStatus.STATUS_EXPLANATION[status])
                    self.update_worker_status(contract_address, TaskStatus.LISTENING)
                elif status == EventListenerStatus.SETUP_FAILED:
                    if self.debug:
                        LogUtils.error(("Status update for contract@" + contract_address + ": " +
                                        EventListenerStatus.STATUS_EXPLANATION[status]))
                    self.update_worker_status(contract_address, TaskStatus.FAILED_TO_REGISTER, debug_msg)
                elif commitments is not None:
                    if self.debug:
                        LogUtils.info("Received commitment with length [" + str(len(commitments)) + "] from contract@" +
                                      contract_address)
                    single_execution_commitment_size = self._get_single_execution_commitment_size(contract_address)
                    if self.debug:
                        LogUtils.info("single_execution_commitment_size for contract:" + contract_address +
                                      " is [" + str(single_execution_commitment_size) + "]")
                    if single_execution_commitment_size is None:
                        LogUtils.error("No single_execution_commitment_size found!")
                        self.update_worker_status(contract_address, TaskStatus.FINISHED)
                    else:
                        single_execution_commitment_length = single_execution_commitment_size * \
                                                             ExecutorConstants.ENCRYPTED_DATA_SIZE
                        if len(commitments) % single_execution_commitment_length != 0:
                            LogUtils.error("Invalid commitment length, cannot be divided by single_execution_commitment"
                                           " size")
                            self.update_worker_status(contract_address, TaskStatus.FINISHED)
                        else:
                            execution_num = int(len(commitments) / single_execution_commitment_length)
                            self.registered_contracts_execution_count[contract_address] = execution_num
                            self.update_worker_status(contract_address, TaskStatus.EXECUTING)
                            for execution_id in range(execution_num):
                                single_execution_commitments = \
                                    commitments[execution_id * single_execution_commitment_length:
                                                (execution_id + 1) * single_execution_commitment_length]
                                if self.debug:
                                    LogUtils.info("Execute commitment[" + str(single_execution_commitments) +
                                                  "] from contract@" + contract_address)
                                self.dispatch_worker(contract_address, execution_id, single_execution_commitments)
                                # Wait for 10 second before staring another worker thread for a new task to avoid too
                                # heavy job.
                                time.sleep(10)

            # Check the result queue.
            if not self.execution_queue.empty():
                execution_result = self.execution_queue.get()
                if self.debug:
                    LogUtils.info('Received execution result' + str(execution_result))
                contract_address = execution_result['contract_address']
                self.registered_contract_verification_result_count[contract_address] += 1
                # If there is any failed execution, need to count down.
                if execution_result['execution_result'] != ExecutionResult.SUCCESS:
                    execution_id = execution_result['execution_id']
                    self.registered_contract_verification_failed_result_count[contract_address][execution_id] = \
                        str(execution_result['execution_result'])
                    if execution_result['debug_msg'] is not None:
                        self.registered_contract_verification_failed_result_count[contract_address][execution_id] += \
                            ' (' + execution_result['debug_msg'] + ')'
                # always update the worker status with EXECUTING after received each execution id's result.
                self.update_worker_status(contract_address, TaskStatus.EXECUTING)
                if self.registered_contract_verification_result_count[contract_address] == \
                   self.registered_contracts_execution_count[contract_address]:
                    self.update_worker_status(contract_address, TaskStatus.FINISHED)
                    # Once finished, cleanup all the execution counters.
                    self.registered_contract_verification_result_count[contract_address] = 0
                    self.registered_contract_verification_failed_result_count[contract_address].clear()
                    self.registered_contracts_execution_count[contract_address] = 0
                    if self.debug:
                        LogUtils.info('Start to clean worker pool for @' + contract_address)
                    self._clean_worker_pool(contract_address)
            time.sleep(1)

    def _clean_worker_pool(self, contract_address):
        cleaned_worker_cnt = 0
        if contract_address in list(self.worker_pool.keys()):
            for execution_id in list(self.worker_pool[contract_address].keys()):
                if not self.worker_pool[contract_address][execution_id].ready():
                    LogUtils.error("Error, worker thread is still live for contract@" + contract_address +
                                   ", execution_id: " + str(execution_id) + ". Force killed")
                    self.worker_pool[contract_address][execution_id].stop()
                self.worker_pool[contract_address][execution_id].join()
                cleaned_worker_cnt += 1
                del self.worker_pool[contract_address][execution_id]
            del self.worker_pool[contract_address]
            if self.debug:
                LogUtils.info('Cleaned ' + str(cleaned_worker_cnt) + ' worker tasks for @' + contract_address)

    def stop(self):
        """
        Stop the executor thread.

        """
        self.should_exit = True

    def should_exit(self):
        return self.should_exit
