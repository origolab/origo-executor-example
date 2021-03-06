class ExecutorConstants:
    """
    The constants used by Executor.
    """
    ENCRYPTED_USER_INPUT_SIZE = 4
    ENCRYPTED_USER_RANDOM_SIZE = 4
    COMMITMENT_HASH_SIZE = 1

    ENCRYPTED_DATA_SIZE = ENCRYPTED_USER_INPUT_SIZE + ENCRYPTED_USER_RANDOM_SIZE + COMMITMENT_HASH_SIZE
