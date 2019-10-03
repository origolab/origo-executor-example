class ExecutionResult:
    """
    The execution result returned by the ExecutionWorker. Executor main thread will use this to check the worker status.
    """
    SUCCESS, FAIL, FAILED_TO_PREPARE, FAILED_TO_GENERATE_PROOF, FAILED_TO_SUBMIT_PROOF, FAILED_TO_DECRYPT,\
        MISS_EXECUTION_INFO, INVALID_COMMITMENTS, HASH_NOT_MATCH = range(9)
    RESULT_EXPLANATION = [
        'worker execution succeed', 'online verification failed', 'worker failed to prepare proof generation', 'worker failed to generate proof',
        'worker failed to submit proof to chain', 'worker failed to decrypt encrypted data', 'missing execution info',
        'invalid input commitment', 'commitment hashes cannot match'
    ]

    @staticmethod
    def get_result_description(result):
        """
        Return the description message for the ExecutionResult.
        Args:
            result: ExecutionResult.

        Returns:
            string, the description of the result.

        """
        return ExecutionResult.RESULT_EXPLANATION[result]
