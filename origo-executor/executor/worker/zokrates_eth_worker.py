from executor.worker.zokrates_worker import ZokratesWorker
from executor.chain_interface.eth_localabi_interface import EthLocalABIInterface
from executor.utils.log_utils import LogUtils
from gevent import sleep
from queue import Queue
import traceback


class ZokratesEthWorker(ZokratesWorker):
    """
    The Worker works for Eth chain and is based on Zokrates.
    """
    def __init__(self, execution_info, chain_config, execution_result_queue, submit_lock=None, debug=False):
        """
        Init the ZokratesEthWorker.
        Args:
            execution_info: dictionary, for all the execution and proof required information.
            chain_config: dictionary, the configuration required by the chain interface.
            execution_result_queue: queue, the queue maintained by the main thread. Worker thread put the execution
                result into the result queue for main thread to check.
            debug: boolean, debug flag.
        """
        ZokratesWorker.__init__(self, execution_info, execution_result_queue, submit_lock, debug)
        self.__chain_interface = EthLocalABIInterface(chain_config)
        self.__verification_result = Queue()
        self.verify_and_settle_event = None

    def submit_proof_to_chain(self, contract_id, execution_id, output, proof):
        """
                Submit the result of the execution and the ZKP proof for the result back to chain.
                Args:
                    contract_id: string, the unique identifier for the contract, it should be a key anchor for the proving key
                        and contract within the proving key path and contract path.
                    execution_id: int, the identity number for different execution of the same contract.
                    output: the result of the final execution.
                    proof: the ZKP proof for the execution result based on the given users' inputs.

                Returns:
                    Boolean, if submission succeeds, then return True, otherwise return False.

                """
        inputs = [int(x) for x in output]
        verification_info = {'inputs': inputs}
        verification_info = {**verification_info, **proof}
        self.verify_and_settle_event = \
            self.__chain_interface.init_verify_and_settle_event_listener(self.contract_address)
        self.__chain_interface.invoke_verify_and_settle(contract_id, execution_id, verification_info)

    def _put_result_into_queue(self, event):
        """
        This is the callback of the VerifyAndSettle event. It puts the verification result info into the event queue.
        Args:
            event: The received event.

        """
        self.__verification_result.put(event.args.success)

    def wait_for_verify_and_settle_event(self, contract_id, execution_id):
        """
        Wait for the verifyAndSettle event from contract and return the result.
        Args:
            contract_id: string, the unique identifier for the contract, it should be a key anchor for the proving key
                and contract within the proving key path and contract path.
            execution_id: int, the identity number for different execution of the same contract.

        Returns:
            Boolean, if verification succeeds, then return True, otherwise return False.

        """
        retry_times = 3
        while retry_times > 0:
            try:
                self.__chain_interface.wait_for_verify_and_settle_event(
                    self.verify_and_settle_event, execution_id,
                    self._put_result_into_queue, self)
                break
            except:
                retry_times = retry_times - 1
                LogUtils.error('failed to wait for settle event, retry remaining %d time(s)' % retry_times)
                if retry_times > 0:
                    traceback.print_exc()
                    LogUtils.info('retrying after 5 seconds')
                    sleep(5)
                else:
                    raise
        return self.__verification_result.get()
