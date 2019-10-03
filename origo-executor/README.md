# Origo Executor
Origo Executor is a python implmenentation of the offline computation node "Executor" defined in the [Origio White Paper](https://origo.network/whitepaper). It listens on commitment openning for registered contracts and do the really execution for the contract as well as generating zero knowledge proof for the final execution result to prove the correctness of its execution.

This repo mainly contains three parts:
1. [Executor](./executor): Python implementation of the offline computation node "Executor" defined in the [Origio White Paper](https://origo.network/whitepaper).

2. [Executor Service](./executor_service): Simple web service to interact with executor, also serve as a dashboard.

3. [Executor Book](./executor_book): Documentation about executor.
   - [Introduction](./executor_book/src/introduction.md)

   - [Getting Started](./executor_book/src/gettingstarted.md)
     - [Configuration and CLI](./executor_book/src/gettingstarted/configuration.md)

   - [Executor Specifications](./executor_book/src/specifications.md)
     - [Workflow](./executor_book/src/specifications/workflow.md)
     - [Contract](./executor_book/src/specifications/contract.md)
     - [Commitment](./executor_book/src/specifications/commitment.md)
