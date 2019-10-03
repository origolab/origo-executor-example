class ExecutorWorkerException(Exception):
    """
    Base class for Executor Worker Exceptions.
    """
    pass


class DecryptionException(ExecutorWorkerException):
    """
    Failed to decrypt data.
    """
    pass


class PreparationException(ExecutorWorkerException):
    """
    Failed to prepare the proof generation.
    """
    pass


class ProofException(ExecutorWorkerException):
    """
    Failed to generate proof.
    """
    pass


class SubmissionException(ExecutorWorkerException):
    """
    Failed to submit proof back to chain.
    """
    pass


class CommitmentValidationFailed(ExecutorWorkerException):
    """
    Invalid commitments.
    """
    pass


class CommitmentHashNotMatch(ExecutorWorkerException):
    """
    The commitments and given hashes do not match.
    """
    pass
