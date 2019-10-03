from abc import abstractmethod
from executor.utils.hash_utils import HashUtils
from executor.worker.executor_worker import ExecutorWorker
from executor.worker.executor_worker_exception import ProofException, PreparationException, CommitmentHashNotMatch
from executor.worker.execution_result import ExecutionResult
from executor.utils.log_utils import LogUtils
from pathlib import Path
from os import path
import json
import subprocess


class ZokratesWorker(ExecutorWorker):
    """
    The Executor Worker based on Zokrates(https://github.com/Zokrates/ZoKrates)
    """
    def __init__(self, execution_info, execution_result_queue, submit_lock=None, debug=False):
        """
        Init ZokratesWorker.
        Args:
            execution_info: dictionary, for all the execution and proof required information.
            execution_result_queue: queue, the queue maintained by the main thread. Worker thread put the execution
                result into the result queue for main thread to check.
            debug: boolean, debug flag.
        """
        ExecutorWorker.__init__(self, execution_info, execution_result_queue, submit_lock, debug)
        try:
            self.__working_path = execution_info['working_path']
        except KeyError:
            self.submit_execution_result(ExecutionResult.MISS_EXECUTION_INFO)
        try:
            self.__proving_key_path = execution_info['proving_key_path']
        except KeyError:
            self.submit_execution_result(ExecutionResult.MISS_EXECUTION_INFO)
        try:
            self.__code_path = execution_info['code_path']
        except KeyError:
            self.submit_execution_result(ExecutionResult.MISS_EXECUTION_INFO)
        try:
            self.__execution_id = execution_info['execution_id']
        except KeyError:
            self.submit_execution_result(ExecutionResult.MISS_EXECUTION_INFO)
        try:
            self.__zokrates_path = execution_info['zokrates_path']
        except KeyError:
            self.submit_execution_result(ExecutionResult.MISS_EXECUTION_INFO)
        try:
            self.__commitments = execution_info['commitments']
        except KeyError:
            self.submit_execution_result(ExecutionResult.MISS_EXECUTION_INFO)

        # self.__field_bit_limit = int(pow(2, 128)) Use Zokrates prime instead
        self.__field_bit_limit = 21888242871839275222246405745257275088548364400416034343698204186575808495616

        # commands need to be run by the workers.
        self.__commands = {}
        self._build_commands()
        if self.debug:
            LogUtils.info("Start to prepare files for ZokratesWorker!")
        self._prepare_files()
        if self.debug:
            LogUtils.info("Finished file preparation!")

    def _run_commands(self, commands, append_str=''):
        """
        List of command keys to run in the given order.
        Args:
            commands: [string], list of command keys.
            append_str: string to append after the commands.

        """
        if self.debug:
            LogUtils.info("Run command: " + str(" && ".join(str(self.__commands[command]) for command in commands)) + append_str)
        process = subprocess.Popen(" && ".join(str(self.__commands[command]) for command in commands), shell=True,
                                   stdout=subprocess.PIPE)
        process.communicate()

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
        cl = len(commitments)
        for i in range(0, cl):
            if skipped_indices is not None and i in skipped_indices:
                continue
            r = randoms[i]
            c_str = "{0:0512b}".format(commitments[i])
            c_1 = (int(c_str[0:128], 2) + r) % self.__field_bit_limit
            c_2 = (int(c_str[128:256], 2) + r) % self.__field_bit_limit
            c_3 = (int(c_str[256:384], 2) + r) % self.__field_bit_limit
            c_4 = (int(c_str[384:512], 2) + r) % self.__field_bit_limit
            oc_str = "{0:0128b}".format(c_1) + "{0:0128b}".format(c_2) + "{0:0128b}".format(c_3) + \
                     "{0:0128b}".format(c_4)
            # now oc_str is a 512 bit string.
            if HashUtils.compute_sha256_for_bitstr(oc_str) != hashes[i]:
                raise CommitmentHashNotMatch

    def generate_commitments(self, biased_commitment, randoms):
        """
        Generate original user commitments with biased commitment and corresponding randoms.
        Args:
            biased_commitment: list of commitments.
            randoms: list of randoms.

        Returns:
            List of original user commitments.

        """
        original_commitments = []
        for i in range(0, len(biased_commitment)):
            r = randoms[i]
            c_str = "{0:0512b}".format(biased_commitment[i])
            c_1 = (int(c_str[0:128], 2) - r) % self.__field_bit_limit
            c_2 = (int(c_str[128:256], 2) - r) % self.__field_bit_limit
            c_3 = (int(c_str[256:384], 2) - r) % self.__field_bit_limit
            c_4 = (int(c_str[384:512], 2) - r) % self.__field_bit_limit
            oc_str = "{0:0128b}".format(c_1) + "{0:0128b}".format(c_2) + "{0:0128b}".format(c_3) + \
                     "{0:0128b}".format(c_4)
            original_commitments.append(int(oc_str, 2))
        return original_commitments

    @staticmethod
    def build_arguments(commitments, randoms, hashes):
        """
        Build the argument input string for Zokrates's compute-witness -a
        Args:
            commitments: list of commitments.
            randoms: list of randoms.
            hashes: list of hashes.

        Returns:
            string, the built argument string.

        """
        commit_array = []
        for i in range(0, len(commitments)):
            # Original commitments and randoms.
            args = []
            bits_str = "{0:0512b}".format(commitments[i])
            args.append(int(bits_str[0:128], 2))
            args.append(int(bits_str[128:256], 2))
            args.append(int(bits_str[256:384], 2))
            args.append(int(bits_str[384:512], 2))
            args.append(randoms[i])
            bits_str = "{0:0256b}".format(hashes[i])
            args.append(int(bits_str[0:128], 2))
            args.append(int(bits_str[128:256], 2))
            commit_array.append(" ".join(str(arg) for arg in args))
        return " ".join(str(arg) for arg in commit_array)

    def _build_commands(self):
        """
        Build the required commands for the ZokratesWorker and add them into the dictionary self.__commands.

        """
        self.__tmp_working_path = path.join(self.__working_path, self.contract_address + "_" + str(self.__execution_id))
        self.__code_path = path.join(self.__working_path, 'compiled_code', self.contract_address) + '_out'
        self.__pk_path = path.join(self.__proving_key_path, self.contract_address) + '.pk'
        self.__var_path = path.join(self.__proving_key_path, self.contract_address) + '.var'
        self.__commands['goto_tmp_working_path'] = 'cd ' + self.__tmp_working_path
        #self.__commands['compile'] = self.__zokrates_path + ' compile -i ' + \
        #                             path.join(self.__tmp_working_path, self.contract_address) + '.code' +\
        #                             ' -o ' + path.join(self.__tmp_working_path, 'out')
        self.__commands['compute_witness'] =\
            self.__zokrates_path + " compute-witness -i " + path.join(self.__tmp_working_path, 'out') + ' -o ' + \
            path.join(self.__tmp_working_path, 'witness') + " -a "
        self.__commands['generate_proof'] = self.__zokrates_path + " generate-proof"
        self.__commands['copy_code'] = 'cp ' + self.__code_path + ' ' + path.join(self.__tmp_working_path, 'out')
        self.__commands['copy_proving_key'] = 'cp ' + self.__pk_path + ' ' + \
                                              path.join(self.__tmp_working_path, 'proving.key')
        self.__commands['copy_variables'] = 'cp ' + self.__var_path + ' ' + \
                                            path.join(self.__tmp_working_path, 'variables.inf')
        self.__commands['build_tmp_working_folder'] = 'mkdir -p ' + self.__tmp_working_path
        self.__commands['rm_tmp_working_folder'] = 'rm -rf ' + self.__tmp_working_path

    def _prepare_files(self):
        """
        Prepare the files required for the execution and proof generation of the worker.

        """
        self._run_commands(['build_tmp_working_folder', 'copy_code', 'copy_proving_key', 'copy_variables'])
        if not self._check_generated_files('prepare'):
            if self.debug:
                LogUtils.info("Failed to copy required files and to finish Zokrates compiling!")
            raise PreparationException

    def _get_output(self):
        """
        Get the output of the execution from witness file.
        Returns:
            list of the output as string.

        """
        witness_path = path.join(self.__tmp_working_path, "witness")
        outputs = {}
        try:
            with open(witness_path) as lines:
                for line in lines:
                    if line.startswith('~out_'):
                        output_index = int(line.split(" ")[0].split("_")[1])
                        outputs[output_index] = line.split(" ")[1].rstrip("\n")
                    else:
                        break
                ret = []
                for index in range(0, len(outputs)):
                    ret.append(outputs[index])
                return ret
        except FileNotFoundError:
            raise ProofException

    def _check_file_exists(self, file_list):
        """
        Check the existence of the files in the list
        Args:
            file_list: [string], file path list to be checked.

        Returns:
            boolean, return True if all the files in the list exists, otherwise return False.

        """
        for file_path in file_list:
            file = Path(file_path)
            if not file.exists():
                if self.debug:
                    LogUtils.info("Missing the required file: " + file_path)
                return False
        return True

    def _check_generated_files(self, step):
        """
        Check the generated files after each Zokrates step.
        Args:
            step: string, the steps includes "prepare", "compute_witness", "generate_proof"

        Returns:
            Return true if all the required files are generated successfully after each step.

        """
        generated_files = []
        if step == 'prepare':
            # proving key file
            generated_files.append(path.join(self.__tmp_working_path, 'proving.key'))
            # variable file
            generated_files.append(path.join(self.__tmp_working_path, 'variables.inf'))
            # out file
            generated_files.append(path.join(self.__tmp_working_path, 'out'))
        elif step == 'compute-witness':
            # witness files
            generated_files.append(path.join(self.__tmp_working_path, 'witness'))
        elif step == 'generate_proof':
            # proof file
            generated_files.append(path.join(self.__tmp_working_path, 'proof.json'))
        return self._check_file_exists(generated_files)

    def _clean_up(self):
        """
        Clean up the intermediate results and files.
        Returns:
            boolean, if succeeds, then return True, otherwise return False.

        """
        self._run_commands(['rm_tmp_working_folder'])
        return not self._check_file_exists([self.__tmp_working_path])

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
        self._run_commands(['goto_tmp_working_path', 'generate_proof'])
        if not self._check_generated_files('generate_proof'):
            raise ProofException
        proof_path = path.join(self.__tmp_working_path, "proof.json")
        try:
            with open(proof_path) as f:
                proof = json.load(f)
                if proof is None or 'proof' not in proof:
                    raise ProofException
                output = self._get_output()
                if not self._clean_up():
                    raise ProofException
                return output, proof['proof']
        except FileNotFoundError:
            raise ProofException

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
        command = self.__zokrates_path + " compute-witness -i " + path.join(self.__tmp_working_path, 'out') + ' -o ' + \
                  path.join(self.__tmp_working_path, 'witness') + " -a " + \
                  self.build_arguments(self.commitments, self.randoms, self.hashes)
        if self.debug:
            LogUtils.info("Run command: " + command)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.communicate()
        #self._run_commands(['compute_witness'],
        #                   self.build_arguments(self.commitments, self.hashes))
        if not self._check_generated_files('compute-witness'):
            raise PreparationException

    @abstractmethod
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
        raise NotImplementedError('Abstract method, not implemented yet')

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
        raise NotImplementedError('Abstract method, not implemented yet')
