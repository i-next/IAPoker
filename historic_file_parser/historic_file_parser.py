import os
import functions.historic_file.convert_file as convert_file
import functions.historic_file.convert_data as convert_data
from .constants import FILE_SOURCE_HISTORIC

def run_parser():
    if not os.path.exists(FILE_SOURCE_HISTORIC):
        print("Le fichier historique.txt n'existe pas.")
        return []
    convert_file_historic = convert_file.convert()
    for tour in convert_file_historic:
        tournaments = convert_data.convert(convert_file_historic)
        break;