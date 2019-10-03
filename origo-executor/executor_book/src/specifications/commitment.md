# Commitment

All the user input for Origo platform is encrypted to guarantee the privacy preserving property.

## Commitment specification

Origo Executor currently support only 512 bits input data. But all the  data must be split into four 128 bits chunks for processing. For example:

- User input `1` should be stored as `0`, `0` `0`, `1` (four 128 bits integer)
- User input `6703903964971298549787012499102923063739682910296196688861780721860882015036773488400937149083451713845015929093243025426876941405973284973216824503042048` (integer for `2^511`) should be stored as `170141183460469231731687303715884105728` (integer for `2^127`), `0`, `0`, `0`.

Assume the four stored user input 128-bit hunck as `input1`, `input2`, `input3`, `input4`, and there is a user generated 1280-bit random `r`, the prime `p` is set to `21888242871839275222246405745257275088548364400416034343698204186575808495616` as imposed by the pairing curve supported by Ethereum, then the commitment (or say the hashing of the user input) should be computed as:

```math
commitment = sha256{(input1 + r) % p || (input12+ r) % p || (input3 + r) % p  || (input4 + r) % p}
```

where the `||` operator is for bit concatenation.

## Data encryption

The input data (512 bits) and the random data (128 bits) should always be stored on the blockchain after RSA encryption. No one but only the Executor which has the corresponding RSA private key for decryption. Origo Executor uses the `1024` bits encryption key and all the data will be encrypted as 1024-bit byte arrays. Still, all of them need to be split into 128 bits chuncks.

## getInputAndCommitment returns

In the [contract](./contract.md) page, the function `getInputAndCommitment` is required to be implemented to return user input and corresponding commitments. It should return an array of uint data. For one single user input, the input data and commitment are actually `9` uints.

```math
encrypted_input_chunck_0 (128 bits), encrypted_input_chunck_1 (128 bits),
encrypted_input_chunck_2 (128 bits), encrypted_input_chunck_3 (128 bits),
encrypted_random_chunck_0 (128 bits), encrypted_random_chunck_1 (128 bits),
encrypted_random_chunck_2 (128 bits), encrypted_random_chunck_3 (128 bits),
commitment (256 bits)
```

After receiving them, Executor first concatenate four chuncks of the encrypted_input_chunck to get encrypted user input, then decrypt to achieve the original user input. Same steps for to decypt the user random. Then the decypted data should always match the commitment by computed as the fomula above.
