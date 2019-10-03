# Getting Started

## Installation

### Docker

Using Docker is currently the recommended way to use Origo Executor.

#### Pre-built Docker image

```bash
docker pull origolab/origo-executor:latest
```

#### Build Docker from source

You can build the container yourself from [source](https://github.com/origolab/origo-executor) with the following commands:

```bash
git clone https://github.com/origolab/origo-executor
cd origo-executor
docker build -t origolab/origo-executor .
```

## Bring up Origo Executor!

You can start the Origo Executor inside the docker with the following command on any port you want:

```bash
$ EXECUTOR_PORT=28888
```
```bash
$ docker run -p $EXECUTOR_PORT:$EXECUTOR_PORT --privileged -ti origolab/origo-executor:latest ./executor_service/run_executor_service.py --service-port=$EXECUTOR_PORT
```
You can open you browser at http://127.0.0.1:28888 to check the current task information of your executor.

You can register contract with http://127.0.0.1:28888/register_contract/0xdaec83836324a0f25B10559a4286015bcbbbA77a

You can unregister contract with http://127.0.0.1:28888/unregister_contract/0xdaec83836324a0f25B10559a4286015bcbbbA77a