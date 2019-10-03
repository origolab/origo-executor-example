import subprocess

from os import path, makedirs


class ZokratesCodeCompiler:
    """
    The code compiler can compile the code Zokrates during the setup phase.
    """
    def __init__(self):
        """
        Init the ZokratesCodeCompiler.

        """
        pass

    @staticmethod
    def compile_code(contract_address, zokrate_path, code_folder, working_folder):
        """
        Compile the target code.
        Args:
            contract_address: string, contract address.
            zokrate_path: string, the path for zokrates binary.
            code_folder: string, the path for the target zokrates code.
            working_folder: string, the working folder.

        Returns:

        """
        compiled_code_folder = path.join(working_folder, 'compiled_code')
        if not path.exists(compiled_code_folder):
            makedirs(compiled_code_folder)
        compile_command = zokrate_path + ' compile -i ' + path.join(code_folder, contract_address) + '.code' + ' -o ' +\
                          path.join(compiled_code_folder, contract_address + '_out')
        process = subprocess.Popen(compile_command, shell=True, stdout=subprocess.PIPE)
        process.communicate()

        # remove the not used file: ...._out.code
        clean_command = 'rm ' + path.join(compiled_code_folder, contract_address + '_out.code')
        process = subprocess.Popen(clean_command, shell=True, stdout=subprocess.PIPE)
        process.communicate()
