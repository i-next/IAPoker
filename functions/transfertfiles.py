import re
from datetime import datetime, timedelta
from pathlib import Path
import shutil

from pony.orm import db_session

import models.tournaments as tournaments

# --- Configuration -----------------------------------------------------
DEFAULT_DEST_DIR = Path(r"D:\IA\Softwares\IA Poker\dataps")

# Dossier(s) surveillé(s) pour de nouveaux tournois. Au démarrage (et à chaque
# clic sur "Rafraîchir"), l'application copie automatiquement vers DEFAULT_DEST_DIR
# tout fichier HH/TS présent ici mais pas encore importé (sans écraser l'existant).
SOURCE_DIRS = [
    # Path(r"C:\Users\euchi\web\statspoker\app\datasrc\psychoman59"),
    Path(r"D:\IA\temp"),
]

TOURNAMENT_ID_PATTERN = re.compile(r"T\d+")

def detect_prefix(filename: str) -> str | None:
    """Retourne 'HH' ou 'TS' selon le début du nom de fichier, sinon None."""
    upper = filename.upper()
    if upper.startswith("HH"):
        return "HH"
    if upper.startswith("TS"):
        return "TS"
    return None

def extract_tournament_id(filename: str) -> str | None:
    """Extrait l'identifiant de tournoi (ex: T4015435195) du nom de fichier."""
    match = TOURNAMENT_ID_PATTERN.search(filename)
    return match.group(0) if match else None

def sync_new_tournaments(source_dirs: list[Path], dest_dir: Path) -> list[str]:
    """Copie vers dest_dir tout fichier HH/TS présent dans source_dirs mais pas
    encore importé (basé sur le nom de destination HH_T<ID>.txt / TS_T<ID>.txt).
    Ne touche jamais aux fichiers déjà présents dans dest_dir (pas d'écrasement).
    Retourne la liste des fichiers nouvellement copiés."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []

    for source_dir in source_dirs:
        if not source_dir.exists():
            continue
        for file_path in source_dir.rglob("*"):  # récursif : trouve aussi les fichiers dans des sous-dossiers
            if not file_path.is_file():
                continue
            prefix = detect_prefix(file_path.name)
            tournament_id = extract_tournament_id(file_path.name)
            # print(tournament_id)
            if prefix is None or tournament_id is None:
                continue

            dest_path = dest_dir / f"{prefix}_{tournament_id}{file_path.suffix or '.txt'}"
            if dest_path.exists():
                continue  # déjà importé, on ne touche pas

            try:
                shutil.copy2(file_path, dest_path)

                now = datetime.now()
                print(int(tournament_id.replace('T', '')) if tournament_id.startswith('T') else int(tournament_id))
                tournament_key = int(tournament_id.replace('T', '')) if tournament_id.startswith('T') else int(tournament_id)
                with db_session():
                    existing = tournaments.Tournament.get(tournament_id=tournament_key)
                    if existing is None:
                        newtour = tournaments.Tournament(
                            tournament_id=tournament_key,
                            date=now.strftime('%Y-%m-%dT%H:%M:%S'),
                            nb_players=0,
                            buy_in_total=0,
                            dotation=0,
                            position=0,
                            gain=0,
                            profit=0,
                            newone=True,
                        )
                    else:
                        existing.date = now.strftime('%Y-%m-%dT%H:%M:%S')
                        existing.nb_players = 0
                        existing.buy_in_total = 0
                        existing.dotation = 0
                        existing.position = 0
                        existing.gain = 0
                        existing.profit = 0
                        existing.newone = True
                        newtour = existing

                copied.append(dest_path.name)
            except OSError:
                pass  # fichier verrouillé/inaccessible : on l'ignore silencieusement

    return copied

def main():
    sync_new_tournaments(SOURCE_DIRS, DEFAULT_DEST_DIR)

if __name__ == "__main__":
    main()