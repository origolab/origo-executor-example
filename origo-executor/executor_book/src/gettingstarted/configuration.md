# Configuration and Commandline tool

Origo Executor provides many configurable settings to ease the usage for different situations.

## `config_file`

You can specifiy the configuration file with this:

```sh
./run_executor_service.py --config-file=/path/to/executor.config
```

The configuration file should be formatted in ```config_name=config_value``` and one configuration in each line, for example:

```text
service_port=28888
account_public_key=0x45cb118D08d0cb4bc3b8E4338635A8BBdF907136
account_private_key=fdc8a9dbfed8638949e642ad4d564683cedf3f484d4ba778e6b22c1bb222ed66
debug_mode=True
```

The configuration in the config file will always be overwritten by the commandline flags. For example,

```sh
./run_executor_service.py --config-file=/path/to/executor.config --debug-mode=False
```

Then the debug_mode will be ```False``` even it is set to True in the configuration file.

## `service_port`

```sh
./run_executor_service.py --service-port=28888
```

The service port can only be an integer between 1 and 65535. Default value is ```5725```.

## `use_existing_data`

```sh
./run_executor_service.py --use-existing-data
```

Whether re-downloading required data for execution if the data already exisits. Default value is ```False```.

For now, the required data including

- contract abi file
- proving key
- zokrates code
- zokrates variable file

The downloaded data will be cleaned up automatically after unregistration.

## `local_proving_key_path`

```sh
./run_executor_service.py --local-proving-key-path='/home/origo/pk'
```

This is the path where the downloaded proving key stored locally. Default value is ```/home/origo-executor/trial/pk```.

## `local_code_path`

```sh
./run_executor_service.py --local-code-path='/home/origo/code'
```

This is the path where the downloaded Zokrates code stored locally. Default value is ```/home/origo-executor/trial/code```.

## `local_abi_path`

```sh
./run_executor_service.py --local-abi-path='/home/origo/abi'
```

This is the path where the downloaded contract abi stored locally. Default value is ```/home/origo-executor/trial/abi```.

## `local_working_path`

```sh
./run_executor_service.py --local-working-path='/home/origo/working'.
```

This is the path where the execution intermediate data stored. Default value is `/home/origo/working`.

## `zokrates_binary_path`

```sh
./run_executor_service.py --zokrates_binary_path='/home/origo/zokrates'
```

This is the path to call Zokrates executable binary. Default value is `/home/origo/zokrates`

## `chain_provider_type`

```sh
./run_executor_service.py --chain-provider-type=http
```

This is the chain provider types, there are three types:

- http
- ipc
- websocket

## `http_uri`

```sh
./run_executor_service.py --http-uri=http://host.docker.internal:7545
```

This is the http uri for chain provider type `http`.

## `ipc_path`

This is the ipc patch for chain provider type `ipc`.

## `websocket_uri`

This is the websocket uri for chain provider type `websocket`.

## `account_private_key`

```sh
./run_executor_service.py --account-private-key=fdc8a9dbfed8638949e642ad4d564683cedf3f484d4ba778e6b22c1bb222ed66
```

This is the execution account private key. Default value is `fdc8a9dbfed8638949e642ad4d564683cedf3f484d4ba778e6b22c1bb222ed66`

## `account_public_key`

```sh
./run_executor_service.py --account-public-key=0x45cb118D08d0cb4bc3b8E4338635A8BBdF907136
```

This is the execution account public key. Default value is `0x45cb118D08d0cb4bc3b8E4338635A8BBdF907136`

## `encryption_type`

```sh
./run_executor_service.py --encryption-type=rsa
```

This is the encryption type used by the executor to decrypt users commitment. For now we only support `rsa` and the Default value is also `rsa`.

## `rsa_key_path`

```sh
./run_executor_service.py --rsa-key-path=/home/origo-executor/private.pem
```

This is the path to the RSA privte key path. The default value is `/home/origo-executor/tmp/private.pem`.

## `listener_poll_interval`

```sh
./run_executor_service.py --listener-poll-interval=1
```

This is the listener poll interval in seconds, which decides the response time once there is commitment opening. Default value is `2` seconds.

## `debug_mode`

```sh
./run_executor_service.py --debug-mode
```

Turn on the debug mode to display more execution informations, which is mainly for development usage.