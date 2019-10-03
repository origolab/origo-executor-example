# Origo Layer 2 Executor With Example
This repository contrains a sample implementation for origo layer 2 [executor](./origo-executor) and an [example](./example-app) application to work with the executor.

Document below will mainly focus on running the executor and related example application, to get start with Origo Executor, please refer [executor book](./origo-executor/executor_book/src/SUMMARY.md)

## Origo Executor
Origo Executor is a python implmenentation of the offline computation node "Executor" defined in the [Origio White Paper](https://origo.network/whitepaper). It listens on commitment openning for registered contracts and do the really execution for the contract as well as generating zero knowledge proof for the final execution result to prove the correctness of its execution.

### Build docker
```bash
$ git clone https://github.com/origolab/origo-executor-example.git
```
```bash
$ cd origo-example
$ docker build -t origolab/origo-executor .
```

### Start Origo Executor server with docker
We prepared a sample [config file](./origo-executor/executor.config) to refer to.
```
service_port=28888
account_public_key=0x1cE571D82989006834D810C377AD562dFEfc9169
account_private_key=3d849e66982b025e87d53dbe57a9170733c3b47643c936af77fcd045a3ac0fea
http_uri=http://host.docker.internal:7545
```

There are several fields you may want to change:
| field               |                definition                |
|---------------------|:----------------------------------------:|
| service_port        |  Port that executor service listening to |
| http_uri            | Http uri for chain provider type `http`. |
| account_public_key  | execution account public key.            |
| account_private_key |      execution account private key.      |

Make sure to change the account public/private key to your own to ensure executor has enough balance to interact with contract.

You can change more config refer to this [configuration document](./origo-executor/executor_book/src/gettingstarted/configuration.md)

Once finishing the configuration setup, you can start executor.

Take default service port 28888 as an example.
```bash
$ EXECUTOR_PORT=28888
```
```bash
$ docker run -p $EXECUTOR_PORT:$EXECUTOR_PORT --privileged -v `pwd`:/config -ti origolab/origo-executor ./executor_service/run_executor_service.py --config-file=/config/executor.config
```
You can open you browser at http://127.0.0.1:28888 to view dashboard of all task information of your executor.

You can register contract with http://127.0.0.1:28888/register_contract/{contract_listen_to}

You can unregister contract with http://127.0.0.1:28888/unregister_contract/{contract_listen_to}

## Example Application
In order to demonstrate how to work with executor, we prepare an example to work with it.

This example is a simple application with max 5 attendants, attendants can input a value and the attendant with the max input will be the winner. This logic can be used for auction, gamble or situation with similar logic.

This application is only used for showing how privacy preserving application working with executor and preserving the privacy.

We won't talk about details of the application logic here, you can always refer to [Origio White Paper](https://origo.network/whitepaper) for the protocol design and check the contract code for [protocol interface](./example-app/contracts/Auction.sol).

To work with this application, you may need to know some basic dApp development.

### Deploy application contract
Make sure to change the truffle [config file](./example-app/truffle.js) to use your account and deploy to the testnet.
```bash
$ cd example-app
$ npm install
$ truffle migrate --reset --network origo
```
After commands above, example application will be deployed to testnet.

### Start application frontend
All frontend logic and related origo libraries can refer to [client code package](./example-app/client).
```bash
$ cd client
$ npm install
$ npm run start
```
Now frontend is started and can be accessd at http://localhost:3000/

On the page, there are four functions: input, create new game, register and unregister. You need to create a new game for every new round, make sure to register the contract after the creation and register the contract after it finishes on executor. You can always refer to http://127.0.0.1:28888 to view executor status.

If you have any problem, feel free to refer to the [code](./origo-executor/executor) and [executor book](./origo-executor/executor_book/src/SUMMARY.md) about executor.