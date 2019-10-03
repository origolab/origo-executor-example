import argparse
from executor.utils.log_utils import LogUtils
from pathlib import Path


class ServiceConfigUtil:
    """
    This is the service config parser for parsing service configurations.
    """

    # Default options for executor service.
    DEFAULT_OPTIONS = {'service_port': 5725,
                       'use_existing_data': False,
                       'local_proving_key_path': '/home/origo-executor/trial/pk',
                       'local_code_path': '/home/origo-executor/trial/code',
                       'local_working_path': '/home/origo/working',
                       'local_abi_path': '/home/origo-executor/trial/abi',
                       'zokrates_binary_path': '/home/origo/zokrates',
                       'chain_provider_type': 'http',
                       'http_uri': 'http://host.docker.internal:7545',
                       'ipc_path': '',
                       'websocket_uri': '',
                       'account_private_key': 'fdc8a9dbfed8638949e642ad4d564683cedf3f484d4ba778e6b22c1bb222ed66',
                       'account_public_key': '0x45cb118D08d0cb4bc3b8E4338635A8BBdF907136',
                       'encryption_type': 'rsa',
                       'rsa_key_path': '/home/origo-executor/tmp/private.pem',
                       'listener_poll_interval': 2}

    def __init__(self):
        """
        Init the ServiceConfigUtil.
        """
        self.options = {}

    def build_configurations(self):
        """
        Generate configuration for executor service.
        Returns:
            dictionary, {string, object}

        """
        parser = argparse.ArgumentParser(description='Origo Executor commandline config.')
        parser.add_argument('--service-port', dest='service_port', type=int,
                            help='The port to start Origo Executor service. Default: ' +
                                 str(self.DEFAULT_OPTIONS['service_port']))
        parser.add_argument('--config-file', dest='config_file_path', type=str,
                            help='The base Origo Executor configuration file path.')
        parser.add_argument('--local-proving-key-path', dest='local_pk_path', type=str,
                            help='The local proving key path to store the downloaded proving keys for contracts. '
                                 'Default: ' + self.DEFAULT_OPTIONS['local_proving_key_path'])
        parser.add_argument('--local-code-path', dest='local_code_path', type=str,
                            help='The local code path to store the downloaded Zokrates code for contracts. '
                                 'Default: ' + self.DEFAULT_OPTIONS['local_code_path'])
        parser.add_argument('--local-working-path', dest='local_working_path', type=str,
                            help='The local working path to generate intermediate data, which is always '
                                 'cleaned up after execution. Default: ' + self.DEFAULT_OPTIONS['local_working_path'])
        parser.add_argument('--local-abi-path', dest='local_abi_path', type=str,
                            help='The local abi path to store the downloaded abi files for contracts. Default: ' +
                                 self.DEFAULT_OPTIONS['local_abi_path'])
        parser.add_argument('--zokrates_binary_path', dest='zokrates_binary_path', type=str,
                            help='The path for Zokrates binary. Default: ' + self.DEFAULT_OPTIONS[
                                'zokrates_binary_path'])

        parser.add_argument('--use-existing-data', dest='use_existing_data', action='store_true', default=None,
                            help='Whether use existing local data and skip downloading again. Default: ' +
                                 str(self.DEFAULT_OPTIONS['use_existing_data']))

        # Chain related args.
        parser.add_argument('--chain-provider-type', dest='chain_provider_type', type=str,
                            help='The block chain provide type: http, ipc, websocket. Default: ' +
                                 self.DEFAULT_OPTIONS['chain_provider_type'])
        parser.add_argument('--http-uri', dest='http_uri', type=str,
                            help='The http uri to connect block chain network. Default: ' + self.DEFAULT_OPTIONS[
                                'http_uri'])
        parser.add_argument('--ipc-path', dest='ipc_path', type=str,
                            help='The ipc path to connect block chain network. Default: ' + self.DEFAULT_OPTIONS[
                                'ipc_path'])
        parser.add_argument('--websocket-uri', dest='websocket_uri', type=str,
                            help='The websocket uri to connect block chain network. Default: ' +
                                 self.DEFAULT_OPTIONS['websocket_uri'])
        parser.add_argument('--account-public-key', dest='account_public_key', type=str,
                            help='The chain account to work with. Default: ' + self.DEFAULT_OPTIONS[
                                'account_public_key'])
        parser.add_argument('--account-private-key', dest='account_private_key', type=str,
                            help='The working account private key. Default: ' + self.DEFAULT_OPTIONS[
                                'account_private_key'])

        # Encryption related args.
        parser.add_argument('--encryption-type', dest='encryption_type', type=str,
                            help='The encryption type used, currently only support: rsa. Default: ' +
                                 self.DEFAULT_OPTIONS['encryption_type'])
        parser.add_argument('--rsa-key-path', dest='rsa_key_path', type=str,
                            help='The RSA private key path. Default: ' + self.DEFAULT_OPTIONS['rsa_key_path'])

        # Listener related args.
        parser.add_argument('--listener-poll-interval', dest='listener_poll_interval', type=int,
                            help='The listener poll interval seconds. Default: ' +
                                 str(self.DEFAULT_OPTIONS['listener_poll_interval']))

        # Debug mode
        parser.add_argument('--debug-mode', dest='debug_mode', action='store_true', default=False,
                            help='Whether enable the debug mode for Origo Executor. Default: False')

        commandline_args = parser.parse_args()

        self._generate_options_from_commandline_args(commandline_args)

    @staticmethod
    def _get_options_from_config_file(config_path):
        parsed_options = {}
        with open(config_path) as f:
            config_lines = f.readlines()
            for line in config_lines:
                config_fields = line.rstrip().split('=')
                if len(config_fields) != 2:
                    LogUtils.error("Invalid config item:" + line)
                    exit(0)
                if config_fields[0] == 'listener_poll_interval' or config_fields[0] == 'service_port':
                    parsed_options[config_fields[0]] = int(config_fields[1])
                elif config_fields[0] == 'use_existing_data' or config_fields[0] == 'debug_mode':
                    if config_fields[1] in ['true', 'True', '1']:
                        parsed_options[config_fields[0]] = True
                    else:
                        parsed_options[config_fields[0]] = False
                else:
                    parsed_options[config_fields[0]] = config_fields[1]
        return parsed_options

    def _generate_options_from_commandline_args(self, input_args):
        """
        Generate the options based on commandline args.
        Args:
            input_args: args of ArgumentParser.

        Returns:

        """
        config_options = {}
        if input_args.config_file_path is not None and input_args.config_file_path != '':
            config_file = Path(input_args.config_file_path)
            if not config_file.is_file():
                LogUtils.error("Could not find provided config file:" + input_args.config_file_path)
                exit(0)
            config_options = self._get_options_from_config_file(input_args.config_file_path)
        for arg in vars(input_args):
            if getattr(input_args, arg) is not None:
                config_options[arg] = getattr(input_args, arg)

        for key, value in self.DEFAULT_OPTIONS.items():
            if key not in config_options or config_options[key] is None:
                config_options[key] = value

        self.options['service_port'] = config_options['service_port']
        self.options['proving_key_path'] = config_options['local_proving_key_path']
        self.options['code_path'] = config_options['local_code_path']
        self.options['working_path'] = config_options['local_working_path']
        self.options['zokrates_path'] = config_options['zokrates_binary_path']
        self.options['abi_path'] = config_options['local_abi_path']
        self.options['chain_config'] = {'provider_type': config_options['chain_provider_type'],
                                        'abi_path': config_options['local_abi_path'],
                                        'private_key': config_options['account_private_key'],
                                        'public_key': config_options['account_public_key'],
                                        'default_account': config_options['account_public_key']}
        self.options['encryption_info'] = {'type': config_options['encryption_type'],
                                           'rsa_key': config_options['rsa_key_path']}
        self.options['poll_interval'] = config_options['listener_poll_interval']
        self.options['use_existing_data'] = config_options['use_existing_data']
        self.options['debug_mode'] = config_options['debug_mode']

        if config_options['chain_provider_type'] == 'http':
            self.options['chain_config']['http_uri'] = config_options['http_uri']
        elif config_options['chain_provider_type'] == 'ipc':
            self.options['chain_config']['ipc_path'] = config_options['ipc_path']
        elif config_options['chain_provider_type'] == 'websocket':
            self.options['chain_config']['websocket_uri'] = config_options['websocket_uri']
        else:
            raise Exception("Unsupported chain provider type:" + config_options['chain_provider_type'])

    def get_options(self):
        LogUtils.info("\nStart the Origo Executor with the following configurations:")
        for key, value in self.options.items():
            LogUtils.info(key + ':\t\t' + str(value))
        return self.options

    def get_service_port(self):
        return self.options['service_port']

    def get_debug_mode(self):
        return self.options['debug_mode']
