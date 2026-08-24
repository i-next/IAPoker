import os
from historic_file_parser.constants import FILE_SOURCE_HISTORIC,PREFIX_TOURNAMENT_HISTORIC_FILE

def convert(file_path = FILE_SOURCE_HISTORIC, prefix = PREFIX_TOURNAMENT_HISTORIC_FILE):
    blocks = []
    current_block = []
    if not os.path.exists(FILE_SOURCE_HISTORIC):
        print("Le fichier historique.txt n'existe pas.")
        return []
    with open(file_path,'r',encoding="utf-8") as file:
        
        for line in file:
            if line.startswith(prefix):               
                if current_block:                    
                    blocks.append(current_block)
                current_block = [line]
            elif current_block:
                # Append to current block if not a new block header
                current_block.append(line)
    if current_block:
        blocks.append(current_block)

    return blocks