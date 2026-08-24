from pathlib import Path
import re
import shutil
TOURNAMENT_ID_PATTERN = re.compile(r"T\d+")
DEFAULT_DEST_DIR = Path(r"D:\IA\Softwares\IA Poker\dataps")
SOURCE_DIRS = [
    Path(r"C:\Users\euchi\web\statspoker\app\datasrc\psychoman59"),
]
class sync_files:

    
    def __init__(self):
        self.SOURCE_DIRS = SOURCE_DIRS
        self.DEFAULT_DEST_DIR = DEFAULT_DEST_DIR
        self.TOURNAMENT_ID_PATTERN = TOURNAMENT_ID_PATTERN


    def detect_prefix(self,filename: str) -> str | None:
        """Retourne 'HH' ou 'TS' selon le début du nom de fichier, sinon None."""
        upper = filename.upper()
        if upper.startswith("HH"):
            return "HH"
        if upper.startswith("TS"):
            return "TS"
        return None

    def extract_tournament_id(self,filename: str) -> str | None:
        """Extrait l'identifiant de tournoi (ex: T4015435195) du nom de fichier."""
        match = self.TOURNAMENT_ID_PATTERN.search(filename)
        return match.group(0) if match else None


    def sync_new_tournaments(self, source_dirs: list[Path]=SOURCE_DIRS, dest_dir: Path=DEFAULT_DEST_DIR) -> list[str]:
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
                prefix = self.detect_prefix(file_path.name)
                tournament_id = self.extract_tournament_id(file_path.name)
                if prefix is None or tournament_id is None:
                    continue

                dest_path = dest_dir / f"{prefix}_{tournament_id}{file_path.suffix or '.txt'}"
                if dest_path.exists():
                    continue  # déjà importé, on ne touche pas

                try:
                    shutil.copy2(file_path, dest_path)
                    copied.append(dest_path.name)
                except OSError:
                    pass  # fichier verrouillé/inaccessible : on l'ignore silencieusement

        return copied

    