# Contract

## Required functions

All the following functions must be implemented for the Origo Executor to do the execution properly.

### getSingleExecutionCommitmentSize

Return the single execution input commitment number. If the received commtiments exceeds this number, they will be divided into different groups for execution and proof generation.

```text
  function getSingleExecutionCommitmentSize() public view returns (uint)
```

### getProvingKeyPath

Return the path to download proving for generating proof for the execution.

```text
  function getProvingKeyPath() view returns (string)
```

### getVariablesPath

Return the path to download variable file (output by Zokrates) for generating proof for the execution.

```text
  function getVariablesPath() view returns (string)
```

### getCodePath

Return the path to download Zokrates code file for generating proof for the execution.

```text
  function getCodePath() view returns (string)
```

### getAbiPath

Return the path to download the contract Abi file for generating proof for the execution.

```text
  function getAbiPath() view returns (string)
```

### getProvingKeySha2

Return the sha256 value for the proving key file.

```text
  function getProvingKeySha2() view returns (uint256)
```

### getCodeSha2

Return the sha256 value for the Zokrates code file.

```text
function getProvingKeyPath() view returns (string)
```

### getVariablesSha2

Return the sha256 value for the variable file.

```text
function getProvingKeyPath() view returns (string)
```

### getAbiSha2

Return the sha256 value for the abi file.

```text
function getProvingKeyPath() view returns (string)
```

### isOpenFinished

Return whether the commitments are open or not now.

```text
function getProvingKeyPath() view returns (string)
```

### getInputAndCommitment

Return the commitments (including encrypted input, encrypted random and commitments(i.e. the hash of the input))

```text
  function getInputAndCommitment() public view returns (uint[])
```

### verifyAndSettle

Verify the proof and settle the result based on the Executor's execution result. 

```text
  function verifyAndSettle(
          uint execution_id,
          uint[2] a,
          uint[2] a_p,
          uint[2][2] b,
          uint[2] b_p,
          uint[2] c,
          uint[2] c_p,
          uint[2] h,
          uint[2] k,
          uint[X] input) public {
              ...
    }
```

The length `X` of the input array can be various for different Dapps.

## Required events

### VerifyAndSettle

All the following events must be implemented for the Origo Executor to do the execution and proof properly.

```text
event VerifyAndSettle(uint execution_id, bool success)
```

Contract should always trigger `VerifyAndSettle(execution_id, true)` if the verification succeeds, otherwise trigger  `VerifyAndSettle(execution_id, false)`.