from executor.zokrates_eth_executor import ZokratesEthExecutor
import time

def generate_worker_options():
    options = {
        'proving_key_path': '/home/origo-executor/trial/pk',
        'code_path': '/home/origo-executor/trial/code',
        'working_path': '/home/origo/working',
        'zokrates_path': '/home/origo/zokrates',
        'abi_path': '/home/origo-executor/trial/abi',
        'chain_config': {'provider_type': 'http', 'http_uri': 'http://host.docker.internal:7545',
                         'abi_path': '/home/origo-executor/trial/abi',
                         'default_abi_path': '/home/origo-executor/trial/abi/default_abi.abi'},
        'encryption_type': 'null',
        'poll_interval': 2,
    }
    return options

def main():
    executor = ZokratesEthExecutor(generate_worker_options(), debug=True)
    executor.start()
    info = {}
    executor.register_contract('0xdaec83836324a0f25B10559a4286015bcbbbA77a', info)

    time.sleep(50)
    executor.unregister_contract('0xdaec83836324a0f25B10559a4286015bcbbbA77a')


if __name__ == "__main__":
    print('start ZokratesEthExecutor')
    main()
