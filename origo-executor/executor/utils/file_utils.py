from os import path, makedirs
from pathlib import Path


class FileUtils:
    @staticmethod
    def create_folders(folder_list):
        """
        make the required folders if they do not exist yet.
        Args:
            folder_list: list of folder paths.

        """
        for folder_path in folder_list:
            if not path.exists(folder_path):
                makedirs(folder_path)

    @staticmethod
    def files_exisit(file_list):
        for file_path in file_list:
            file = Path(file_path)
            if not file.is_file():
                return False
        return True
