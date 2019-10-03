from abc import abstractmethod
from executor.constants.executor_constants import ExecutorConstants
from executor.worker.decryptor.rsa_decryptor import RSADecryptor
from executor.worker.decryptor.null_decryptor import NullDecryptor
from executor.worker.execution_result import ExecutionResult
from executor.worker.executor_worker_exception import DecryptionException, \
    PreparationException, ProofException, SubmissionException, CommitmentHashNotMatch, CommitmentValidationFailed
from executor.utils.data_utils import DataUtils
from executor.utils.log_utils import LogUtils
from gevent import Greenlet


class ExecutorWorker(Greenlet):
    """
    Executor base class.
    """

    def __init__(self, execution_info, execution_result_queue, submit_lock=None, debug=False):
        """
        Init the Executor.
        Args:
            execution_info: dictionary, for all the execution and proof required information.
            execution_result_queue: queue, the queue maintained by the main thread. Worker thread put the execution
                result into the result queue for main thread to check.
            debug: boolean, debug flag.
        """
        Greenlet.__init__(self)
        # This is the queue for putting execution result into for the main thread to check.
        self.__execution_result_queue = execution_result_queue
        self.debug = debug
        self.__should_exit = False

        assert 'encryption_info' in execution_info
        encryption_info = execution_info['encryption_info']
        self.__decryptor = None
        if encryption_info['type'] == 'ecdsa':
            raise NotImplementedError("ECDSA encryption is not supported yet. Use RSA")
        elif encryption_info['type'] == 'rsa':
            assert 'rsa_key' in encryption_info
            self.__decryptor = RSADecryptor(encryption_info['rsa_key'])
        elif encryption_info['type'] == 'null':
            self.__decryptor = NullDecryptor()
        else:
            raise Exception("Not supported encryption type:" + encryption_info['type'])

        assert 'commitments' in execution_info
        self.__encrypted_commitments = execution_info['commitments']

        assert 'contract_address' in execution_info
        self.contract_address = execution_info['contract_address']

        if 'execution_id' in execution_info and execution_info['execution_id'] is not None:
            self.__execution_id = execution_info['execution_id']
        else:
            self.__execution_id = None

        self.submit_lock = submit_lock
        self.commitments = None
        self.randoms = None
        self.hashes = None

    def decrypt_inputs(self, encrypted_private_inputs, skipped_indices):
        """
        Decrypt the encrypted inputs from users.
        Args:
            encrypted_private_inputs: list, encrypted user inputs.
            skipped_indices: list, the indices of elements in the list that should be skipped decryption and keep
                the original.
        Returns:
            List, the decrypted users' private inputs in the same order as the original encrypted list.
        """
        decrypted_ret = []
        commitment_size = len(encrypted_private_inputs) / 2
        for index in range(len(encrypted_private_inputs)):
            try:
                datum = encrypted_private_inputs[index]
                if skipped_indices is not None and (index % commitment_size) in skipped_indices:
                    decrypted_ret.append(datum)
                else:
                    decrypted_datum = self.__decryptor.decrypt(datum)
                    decrypted_ret.append(decrypted_datum)
            except Exception:
                raise DecryptionException
        return decrypted_ret

    @abstractmethod
    def generate_proof(self, contract_id, execution_id):
        """
        Generate the proof for the target contract id with given inputs.
        Args:
            contract_id: string, the unique identifier for the contract, it should be a key anchor for the proving key
                and contract within the proving key path and contract path.
            execution_id: string, the identity number for different execution of the same contract.

        Returns:
            The ZKP proof for the target contract with given inputs.

        """
        raise NotImplementedError('Abstract method, not implemented yet')

    @abstractmethod
    def prepare_proof_generation(self, contract_id, execution_id):
        """
        Prepare the proof generation. May include (but not limited to) the following processes:
        * Input data pre-processing.
        * Contract execution.
        * Witness generation.
        Args:
            contract_id: string, the unique identifier for the contract, it should be a key anchor for the proving key
                and contract within the proving key path and contract path.
            execution_id: string, the identity number for different execution of the same contract.

        Returns:
            Boolean, if preparation succeeded, return True, otherwise return False.

        """
        raise NotImplementedError('Abstract method, not implemented yet')

    @abstractmethod
    def submit_proof_to_chain(self, contract_id, execution_id, output, proof):
        """
        Submit the result of the execution and the ZKP proof for the result back to chain.
        Args:
            contract_id: string, the unique identifier for the contract, it should be a key anchor for the proving key
                and contract within the proving key path and contract path.
            execution_id: string, the identity number for different execution of the same contract.
            output: the result of the final execution.
            proof: the ZKP proof for the execution result based on the given users' inputs.

        Returns:
            Boolean, if submission succeeds, then return True, otherwise return False.

        """
        raise NotImplementedError('Abstract method, not implemented yet')

    @abstractmethod
    def wait_for_verify_and_settle_event(self, contract_id, execution_id):
        """
        Wait for the verifyAndSettle event from contract and return the result.
        Args:
            contract_id: string, the unique identifier for the contract, it should be a key anchor for the proving key
                and contract within the proving key path and contract path.
            execution_id: string, the identity number for different execution of the same contract.

        Returns:
            Boolean, if verification succeeds, then return True, otherwise return False.

        """
        raise NotImplementedError('Abstract method, not implemented yet')

    def submit_execution_result(self, execution_result, debug_msg=None):
        """
        Submit the execution result back to the main thread.
        Args:
            execution_result: ExecutionResult.
            debug_msg: string, the additional info for the execution result if not None

        """
        debug_str = ExecutionResult.get_result_description(execution_result)
        if debug_msg is not None:
            debug_str += (', ' + debug_msg)
        result = {'execution_result': execution_result, 'contract_address': self.contract_address,
                  'execution_id': self.__execution_id, 'debug_msg': debug_str}
        self.__execution_result_queue.put(result)

    def _check_commitments_validation(self, inputs):
        """
        Check the validation of the input commitments.
        Args:
            inputs: list, half of the input are commitments, the other half left are hashes. The commitments contain
                actually the real user input and a random value that only user knows.

        Returns:
            commitments, randoms and hashes.

        """
        cl = len(inputs)
        commitments = []
        randoms = []
        hashes = []
        if cl == 0 or cl % ExecutorConstants.ENCRYPTED_DATA_SIZE != 0:
            raise CommitmentValidationFailed
        for i in range(0, cl, ExecutorConstants.ENCRYPTED_DATA_SIZE):
            commitments.append(DataUtils.concatenate_split_data(
                inputs[i: i + ExecutorConstants.ENCRYPTED_USER_INPUT_SIZE],
                int(1024 / ExecutorConstants.ENCRYPTED_USER_INPUT_SIZE)))
            randoms.append(DataUtils.concatenate_split_data(
                inputs[i + ExecutorConstants.ENCRYPTED_USER_INPUT_SIZE:
                       i + ExecutorConstants.ENCRYPTED_USER_INPUT_SIZE +
                       ExecutorConstants.ENCRYPTED_USER_RANDOM_SIZE],
                int(1024 / ExecutorConstants.ENCRYPTED_USER_RANDOM_SIZE)))
            hashes.append(DataUtils.concatenate_split_data(
                inputs[i + ExecutorConstants.ENCRYPTED_USER_INPUT_SIZE +
                       ExecutorConstants.ENCRYPTED_USER_RANDOM_SIZE:
                       i + ExecutorConstants.ENCRYPTED_USER_INPUT_SIZE + ExecutorConstants.ENCRYPTED_USER_RANDOM_SIZE +
                       ExecutorConstants.COMMITMENT_HASH_SIZE],
                int(256 / ExecutorConstants.COMMITMENT_HASH_SIZE)))
        return commitments, randoms, hashes

    @staticmethod
    def _find_skipped_commitment_indices(commitments, randoms, hashes):
        """
        Prepare the inputs from the given commitments.
        Args:
            commitments: list, commitments.
            randoms: list, random values.
            hashes: list, hash value of commitments.
        Returns:
            list, the indices that should be skipped for decryption and hash checking.
        """
        skipped_indices = []
        for i in range(len(commitments)):
            if commitments[i] == randoms[i] == hashes[i]:
                skipped_indices.append(i)
        return skipped_indices

    def check_commitments(self, commitments, randoms, hashes, skipped_indices):
        """
        Prepare the inputs from the given commitments.
        Args:
            commitments: list, commitments.
            randoms: list, random values.
            hashes: list, hash value of commitments.
            skipped_indices: list, indices of elements that should be skipped for the checking.

        Returns:

        """
        raise NotImplementedError('Abstract method, not implemented yet')

    def generate_commitments(self, biased_commitment, randoms):
        """
        Generate original user commitments with biased commitment and corresponding randoms.
        Args:
            biased_commitment: list of commitments.
            randoms: list of randoms.

        Returns:
            List of original user commitments.

        """
        raise NotImplementedError('Abstract method, not implemented yet')

    def _run(self):
        """
        Finish the execution and proof generation and submit all the result back to block chain.

        """
        if self.debug:
            LogUtils.info("Start to check commitment validation")
        try:
            commitments, randoms, self.hashes = self._check_commitments_validation(self.__encrypted_commitments)
        except CommitmentValidationFailed:
            self.submit_execution_result(ExecutionResult.INVALID_COMMITMENTS)
            return
        if self.debug:
            LogUtils.info("Start to decrypt")
        try:
            if self.debug:
                LogUtils.info("Input encrypted commitment:" + str(commitments))
                LogUtils.info("Input encrypted random:" + str(randoms))
            # find out the data that should be skipped: if the commitment, random and hash are all the same value, then
            # the decryption and hash check will be skipped for those input.
            skipped_indices = self._find_skipped_commitment_indices(commitments, randoms, self.hashes)
            decrypted_commitments_and_randoms = self.decrypt_inputs(commitments + randoms, skipped_indices)
            half = int(len(decrypted_commitments_and_randoms) / 2)
            self.commitments = decrypted_commitments_and_randoms[:half]
            self.randoms = decrypted_commitments_and_randoms[half:]
            if self.debug:
                LogUtils.info("Input decrypted commitment:" + str(self.commitments))
                LogUtils.info("Input decrypted random:" + str(self.randoms))
        except DecryptionException:
            self.submit_execution_result(ExecutionResult.FAILED_TO_DECRYPT)
            return
        if self.debug:
            LogUtils.info("Start to check sha256 of commitments")
        try:
            self.check_commitments(self.commitments, self.randoms, self.hashes, skipped_indices)
        except CommitmentHashNotMatch:
            self.submit_execution_result(ExecutionResult.HASH_NOT_MATCH)
            return
        if self.debug:
            LogUtils.info("Start to prepare proof")
        try:
            self.prepare_proof_generation(self.contract_address, self.__execution_id)
        except PreparationException:
            self.submit_execution_result(ExecutionResult.FAILED_TO_PREPARE)
            return
        if self.debug:
            LogUtils.info("Start to generate_proof")
        try:
            output, proof = self.generate_proof(self.contract_address, self.__execution_id)
            if self.debug:
                LogUtils.info('output is:' + str(output))
                LogUtils.info('proof is:' + str(proof))
        except ProofException:
            self.submit_execution_result(ExecutionResult.FAILED_TO_GENERATE_PROOF)
            return
        if self.debug:
            LogUtils.info("Start to submit proof")
        try:
            if self.submit_lock and self.submit_lock.acquire():
                try:
                    self.submit_proof_to_chain(self.contract_address, self.__execution_id, output, proof)
                finally:
                    self.submit_lock.release()
            else:
                self.submit_proof_to_chain(self.contract_address, self.__execution_id, output, proof)
        except SubmissionException:
            self.submit_execution_result(ExecutionResult.FAILED_TO_SUBMIT_PROOF)
            return
        if self.debug:
            LogUtils.info("Finished proof submission, waiting for VerifyAndSettleEvent")
        verification_result = self.wait_for_verify_and_settle_event(self.contract_address, self.__execution_id)
        if verification_result:
            if self.debug:
                LogUtils.info("Online verification succeeded.")
            self.submit_execution_result(ExecutionResult.SUCCESS)
        else:
            if self.debug:
                LogUtils.info("Online verification failed.")
            self.submit_execution_result(ExecutionResult.FAIL)

    def should_exit(self):
        return self.__should_exit

    def stop(self):
        self.__should_exit = True
