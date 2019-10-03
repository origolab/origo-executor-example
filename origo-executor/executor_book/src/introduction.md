# Introduction

Origo Executor is the python implmenentation of the offline computation node "Executor" defined in the [Origio White Paper](https://origo.network/whitepaper). It listens on commitment openning for registered contracts and do the really execution for the contract as well as generating zero knowledge proof for the final execution result to prove the correctness of its execution.

## Background on zero knowledge proof (ZKP)

ZKP is a well established method in cryptography. In ZKP, there are two parties, one called prover can prove to another party, called verifier, some statements holds without sharing any information about why it holds. ZKP protocol must satisfy the following three properties:

* **Completeness**: given honest prover and honest verifier, the protocol succeeds with overwhelming probability.

* **Soundness**: no one who does not know the secret can convince the verifier with the non-negligible probability.

* **Zero Knowledge**: the proof does not leak any additional information.

## License

Origo Executor is released under the GNU General Public License v3.