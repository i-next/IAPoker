import os
from pathlib import Path
from .constants import DEFAULT_DEST_DIR
import functions.data_to_tournament as data_to_tournament


class new_files_parser:
    def __init__(self):
        self.DEFAULT_DEST_DIR = DEFAULT_DEST_DIR

    def add_new_files(self,list_files:list):
        # print(list_files)
        # print(self.DEFAULT_DEST_DIR)
        for file in list_files:
            file_path = os.path.join(self.DEFAULT_DEST_DIR, file)
            if not os.path.isfile(file_path):
                continue
            if file.startswith('TS'):
                text = Path(file_path).read_text(encoding="utf-8")
                lines = text.splitlines()
                data_to_convert = data_to_tournament.data_to_tournament()
                data_to_convert.set_entity_tournament(lines)
                # print(lines)