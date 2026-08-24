from pathlib import Path
import os
import re
import functions.extract_tournament_info as extract_tournament_info
class sync_history_file:

    def __init__(self, file_path: str = "historique.txt"):
        self.file_path = file_path
        

    def read_history(self) -> list[str]:
        """Lit le fichier historique.txt et retourne la liste des lignes."""
        if not os.path.exists(self.file_path):
            print("Le fichier historique.txt n'existe pas.")
            return []
        convert_history = self.convert_history_to_list()
        
        self.add_new_tournament(convert_history)

    def convert_history_to_list(self, prefix="PokerStars Tournoi") -> list[str]:
        """Lit le fichier historique.txt et retourne la liste des lignes."""
        blocks = []
        current_block = []
        with open(self.file_path, 'r', encoding='utf-8') as file:
            for line in file:
            # If line starts with the prefix, finalize previous block if exists
                if line.startswith(prefix):
                    if current_block:
                        blocks.append(current_block)
                    current_block = [line]
                elif current_block:
                    # Append to current block if not a new block header
                    current_block.append(line)
        
        # Append the last block
        if current_block:
            blocks.append(current_block)
            
        return blocks

    def add_new_tournament(self, tournament_data: list[str]) -> None:
        """Ajoute un nouveau tournoi à la fin du fichier historique.txt."""
        for line in tournament_data:       
            print(line)     
            extractor = extract_tournament_info.extract_tournament_info(line)
            info_tournament = extractor.extract_info()
            print(info_tournament)