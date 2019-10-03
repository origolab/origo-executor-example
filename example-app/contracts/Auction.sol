pragma solidity ^0.5.0;

import "./IVerifier.sol";

contract Auction {
  struct Commit {
    bool hasCommit;
    uint128 commitPart1;
    uint128 commitPart2;
  }

  struct Input {
    bool hasInput;
    uint[4] encryptedVote;
    uint[4] encryptedRandom;
  }

  address owner;
  IVerifier verifier;
  address[] users;
  mapping (address => Commit) commits;
  mapping (address => Input) inputs;
  mapping (address => uint) balances;
  uint userCount = 0;
  uint openCount = 0;
  uint maxUserCount = 5;
  address winner;

  bool isGameOver = false;
  uint startTime = 0;
  uint commitTimeout = 1 minutes;
  uint openTimeout = 1 minutes;

  uint256 single_execution_commitment_size = 5;

  event VerifyAndSettle(uint execution_id, bool success);

  string proving_key_path = "https://s3.amazonaws.com/origo.executor/max5/proving.key";
  string code_path = "https://s3.amazonaws.com/origo.executor/max5/max5_empty_input.code";
  string variables_path = "https://s3.amazonaws.com/origo.executor/max5/variables.inf";
  string abi_path = "https://s3.amazonaws.com/origo.executor/max5/max5.abi";
  uint256 pk_sha2 = 83574262285087747409869274578867297246033083182810418971158615318742077761780;
  uint256 code_sha2 = 44921137919122833048385687679121061102645800642090071779680072055047123980585;
  uint256 variables_sha2 = 72344893535488493447883533111635506465859174117969165997763546235039059916463;
  uint256 abi_sha2 = 55596027210539693694777635839082215033061808174322349786920672458634072287404;

  constructor(address _owner, address _verifier) public {
    owner = _owner;
    verifier = IVerifier(_verifier);
  }

  function submitInput(uint[4] memory encryptedVote, uint[4] memory encryptedRandom) public {
    require(inputs[msg.sender].hasInput == false, "You have already submited input!");
    inputs[msg.sender] = Input(true, encryptedVote, encryptedRandom);
    openCount++;
  }

  function submitCommit(uint128 commitPart1, uint128 commitPart2) public payable {
    require(commits[msg.sender].hasCommit == false, "You have already submited commitments!");
    commits[msg.sender] = Commit(true, commitPart1, commitPart2);
    userCount++;
    users.push(msg.sender);
    balances[msg.sender] = msg.value;

    // In this case, the first user's commit means the start of the vote.
    if (startTime == 0) {
      startTime = block.timestamp;
    }
  }

  function submitCommitAndInput(uint[4] memory encryptedVote, uint[4] memory encryptedRandom, uint128 commitPart1, uint128 commitPart2)
   public payable {
    submitCommit(commitPart1, commitPart2);
    submitInput(encryptedVote, encryptedRandom);
  }

  function isCommitFinished() public view returns (bool) {
    return userCount == maxUserCount || (startTime > 0 && block.timestamp >= startTime + commitTimeout);
  }

  function isOpenFinished() public view returns (bool) {
    return !isGameOver && ((userCount > 0 && maxUserCount == openCount) || (startTime > 0 && block.timestamp >= startTime + commitTimeout + openTimeout));
  }

  function isInputSubmitted(address user) public view returns (bool) {
    return inputs[user].hasInput == true;
  }

  function isCommitSubmitted(address user) public view returns (bool) {
    return commits[user].hasCommit == true;
  }

  function getInputAndCommitment() public view returns (uint[] memory) {
    require(isOpenFinished(), "Not all users open their inputs and it's not timed out.");
    uint resultLength = ((users.length + single_execution_commitment_size - 1) / single_execution_commitment_size) * single_execution_commitment_size;
    uint[] memory result = new uint[](resultLength * 9);
    for (uint i = 0; i < users.length; i++) {
      for (uint j = 0; j < 4; j++) {
        result[i * 9 + j] = inputs[users[i]].encryptedVote[j];
        result[i * 9 + 4 + j] = inputs[users[i]].encryptedRandom[j];
      }
      result[i * 9 + 8] = uint(commits[users[i]].commitPart1) * (2 ** 128) + uint(commits[users[i]].commitPart2);
    }
    return result;
  }

  function getUserCount() public view returns (uint) {
    return userCount;
  }

  function getOpenCount() public view returns (uint) {
    return openCount;
  }

  function getResult() public view returns (address) {
    return winner;
  }

  function getSingleExecutionCommitmentSize() public view returns (uint) {
    return single_execution_commitment_size;
  }

  function getProvingKeyPath() public view returns (string memory) {
    return proving_key_path;
  }

  function getVariablesPath() public view returns (string memory) {
    return variables_path;
  }

  function getCodePath() public view returns (string memory) {
    return code_path;
  }
 
  function getAbiPath() public view returns (string memory) {
    return abi_path;
  }

  function getProvingKeySha2() public view returns (uint256) {
    return pk_sha2;
  }

  function getCodeSha2() public view returns (uint256) {
    return code_sha2;
  }

  function getVariablesSha2() public view returns (uint256) {
    return variables_sha2;
  }

  function getAbiSha2() public view returns (uint256) {
    return abi_sha2;
  }

  function getIsGameOver() public view returns (bool) {
    return isGameOver;
  }

  function settleResult(uint winnerIndex, uint bid) internal {
    if (winnerIndex != 0) {
      winner = users[winnerIndex - 1];
    }
  }

  function verifyAndSettle(
    uint execution_id,
    uint[2] memory a,
    uint[2] memory a_p,
    uint[2][2] memory b,
    uint[2] memory b_p,
    uint[2] memory c,
    uint[2] memory c_p,
    uint[2] memory h,
    uint[2] memory k,
    uint[2] memory input) public {
    uint _execution_id = execution_id;
    uint[] memory inputValues = new uint[](single_execution_commitment_size * 2 + input.length);
    for (uint i = 0; i < single_execution_commitment_size; i++) {
      if (_execution_id * single_execution_commitment_size + i < users.length) {
        address user = users[_execution_id * single_execution_commitment_size + i];
        inputValues[i * 2] = uint(commits[user].commitPart1);
        inputValues[i * 2 + 1] = uint(commits[user].commitPart2);
      }
    }
    for (uint i = 0; i < input.length; i++) {
      inputValues[single_execution_commitment_size * 2 + i] = input[i];
    }

    if (verifier.verifyTx(a, a_p, b, b_p, c, c_p, h, k, inputValues)) {
      emit VerifyAndSettle(_execution_id, true);

      isGameOver = true;
      settleResult(input[0], input[1]);
    } else {
      emit VerifyAndSettle(_execution_id, false);
    }
  }
}