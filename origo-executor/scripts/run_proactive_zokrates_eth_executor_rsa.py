from gevent import monkey, signal, kill
monkey.patch_all()

import time
from executor.zokrates_proactive_eth_executor import ZokratesProactiveEthExecutor
from scripts.graceful_killer import GracefulKiller

def generate_worker_options():
    options = {
        'proving_key_path': '/home/origo-executor/trial/pk',
        'code_path': '/home/origo-executor/trial/code',
        'working_path': '/home/origo/working',
        'zokrates_path': '/home/origo/zokrates',
        'abi_path': '/home/origo-executor/trial/abi',
        'chain_config': {'provider_type': 'http', 'http_uri': 'http://host.docker.internal:7545',
                         'abi_path': '/home/origo-executor/trial/abi',
                         'private_key': 'fdc8a9dbfed8638949e642ad4d564683cedf3f484d4ba778e6b22c1bb222ed66',
                         'public_key': '0x45cb118D08d0cb4bc3b8E4338635A8BBdF907136',
                         'default_account': '0x45cb118D08d0cb4bc3b8E4338635A8BBdF907136'},
        'encryption_info': {'type':'rsa', 'rsa_key': '/home/origo-executor/tmp/private.pem'},
        'poll_interval': 2,
    }
    return options


def main():
    executor = ZokratesProactiveEthExecutor(generate_worker_options(), debug=True)
    executor.start()
    info = {}
    executor.register_contract('0xdaec83836324a0f25B10559a4286015bcbbbA77a', info)

    time.sleep(50)
    executor.unregister_contract('0xdaec83836324a0f25B10559a4286015bcbbbA77a')
    killer = GracefulKiller()
    while not killer.kill_now:
        time.sleep(2)

    executor.stop()
    executor.join()


if __name__ == "__main__":
    print('start ZokratesEthExecutor')
    main()
