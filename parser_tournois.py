"""
Parser de tournois PokerStars (fichiers TS_*.txt)
→ Extraction : ID, date, joueurs, buy-in total, dotation, position finale, gain
→ Stockage dans une base SQLite intégrée (tournaments.db)
"""

import os
import re
import sqlite3 # to delete
from datetime import datetime
from pathlib import Path
import historic_file_parser.sync_files as sync_files  
import sync_history_file
import functions.extract_tournament_info as extract_tournament_info
import functions.db_functions as db_functions


# ---------------------------------------------------------------------------
# 1. Configuration
# ---------------------------------------------------------------------------
DB_PATH = "tournaments.db" # to delete
NICKNAME = "psychoman59"


# ---------------------------------------------------------------------------
# 2. Initialisation de la base de données
# ---------------------------------------------------------------------------

# def init_db():
#     """Crée les tables SQLite nécessaires et migre la table tournaments si besoin."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("PRAGMA foreign_keys = ON")
#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS tournaments (
#             id            INTEGER PRIMARY KEY,
#             tournament_id TEXT    UNIQUE NOT NULL,
#             date          TEXT    NOT NULL,
#             nb_players    INTEGER NOT NULL,
#             buy_in_total  REAL    NOT NULL,
#             dotation      REAL    NOT NULL,
#             position      INTEGER,
#             gain          REAL    DEFAULT 0,
#             profit        REAL    DEFAULT 0
#         )
#         """
#     )
#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS countrycity (
#             id   INTEGER PRIMARY KEY,
#             name TEXT    UNIQUE NOT NULL
#         )
#         """
#     )
#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS players (
#             id             INTEGER PRIMARY KEY,
#             pseudo         TEXT    NOT NULL UNIQUE,
#             type           TEXT,
#             id_countrycity INTEGER,
#             nbTour         INTEGER DEFAULT 0,
#             FOREIGN KEY(id_countrycity) REFERENCES countrycity(id)
#         )
#         """
#     )
#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS tournament_players (
#             id            INTEGER PRIMARY KEY,
#             tournament_id INTEGER NOT NULL,
#             player_id     INTEGER NOT NULL,
#             UNIQUE(tournament_id, player_id),
#             FOREIGN KEY(tournament_id) REFERENCES tournaments(id),
#             FOREIGN KEY(player_id) REFERENCES players(id)
#         )
#         """
#     )
#     # TODO: Create table tournament in android
#     cursor.execute(
#             """
#             CREATE TABLE IF NOT EXISTS tournaments_not_stored (
#                 id            INTEGER PRIMARY KEY,
#                 tournament_id TEXT    UNIQUE NOT NULL,
#                 date          TEXT    NOT NULL,
#                 nb_players    INTEGER NOT NULL,
#                 buy_in_total  REAL    NOT NULL,
#                 dotation      REAL    NOT NULL,
#                 position      INTEGER,
#                 gain          REAL    DEFAULT 0,
#                 profit        REAL    DEFAULT 0
#             )
#             """
#         )


#     # Migration : ajouter les colonnes gain et profit si la table existait avant
#     cursor.execute("PRAGMA table_info(tournaments)")
#     columns = [row[1] for row in cursor.fetchall()]
#     if "gain" not in columns:
#         cursor.execute("ALTER TABLE tournaments ADD COLUMN gain REAL DEFAULT 0")
#     if "profit" not in columns:
#         cursor.execute("ALTER TABLE tournaments ADD COLUMN profit REAL DEFAULT 0")
#     cursor.execute("PRAGMA table_info(players)")
#     player_columns = [row[1] for row in cursor.fetchall()]
#     if "nbTour" not in player_columns:
#         cursor.execute("ALTER TABLE players ADD COLUMN nbTour INTEGER DEFAULT 0")
#     conn.commit()
#     conn.close()


# ---------------------------------------------------------------------------
# 3. Parsing d'un fichier TS
# ---------------------------------------------------------------------------

def parse_tournament_file(filepath: Path, Tournament: object = None) -> dict | None:
    """
    Parse un fichier TS_*.txt et retourne un dict avec les champs extraits.
    Retourne None si le fichier est invalide.
    """
    text = filepath.read_text(encoding="utf-8")

    tournament = Tournament(44584,"testdate",3,0.5,1.5,1,1.5,1)
    print(tournament)
    
    lines = text.splitlines()
    print("test obj",extract_tournament_info.extract_tournament_info(text).tournament_data)
    data = extract_tournament_info.extract_tournament_info(text).extract_info()
    print("data from file",data)
    # info = data.extract_info()
    
    if not lines:
        return None

    # --- ID du tournoi (ligne 1) ---
    id_match = re.search(r"#(\d+)", lines[0])
    if not id_match:
        return None
    tournament_id = id_match.group(1)

    # --- Buy-in (ligne 2) : "Buy-in : €0.93/€0.07 EUR" ---
    buy_in_total = 0.0
    if len(lines) > 1:
        for i in range(10):
            buy_match = re.findall(r"€([0-9]+[.,]?[0-9]*)", lines[i])
            if buy_match and re.search(r'\bbuy-in\b', lines[i], re.IGNORECASE):
                buy_in_total = sum(
                    float(m.replace(",", ".")) for m in buy_match
                )
                break
        #buy_match = re.findall(r"€([0-9]+[.,]?[0-9]*)", lines[1])
        if buy_match:
            buy_in_total = sum(
                float(m.replace(",", ".")) for m in buy_match
            )

    # --- Nombre de joueurs (ligne 3) ---
    nb_players = None
    if len(lines) > 2:
        for i in range(10):
            players_match = re.search(r"(\d+)\s+joueurs?", lines[i], re.IGNORECASE)
            if players_match:
                nb_players = int(players_match.group(1))
                break        
        if not players_match:
            print(f"[WARN] {filepath.name} — nombre de joueurs non détecté")
    # --- Dotation (ligne 4) : "Dotation totale : €3.00 EUR" ---
    dotation = 0.0
    if len(lines) > 3:
        dot_match = re.search(r"€([0-9]+[.,]?[0-9]*)", lines[3])
        if dot_match:
            dotation = float(dot_match.group(1).replace(",", "."))

    # --- Date : priorité à la ligne 5, sinon recherche sur toute la fiche ---
    date_str = None
    date_match = None
    if len(lines) > 4:
        date_match = re.search(r"(\d{2}/\d{2}/\d{4}\s+\d{1,2}:\d{2}:\d{2})", lines[4])
    if not date_match:
        for line in lines:
            if "Tournoi commencé" in line:
                date_match = re.search(r"(\d{2}/\d{2}/\d{4}\s+\d{1,2}:\d{2}:\d{2})", line)
                if date_match:
                    break
    if date_match:
        raw = date_match.group(1)
        dt = datetime.strptime(raw, "%d/%m/%Y %H:%M:%S")
        date_str = dt.isoformat()

    # --- Position finale ---
    position = None
    pos_match = re.search(
        r"Vous avez terminé à la (\d+)(?:er|e|ème|eme)? place", text, re.IGNORECASE
    )
    if pos_match:
        position = int(pos_match.group(1))

    # --- Gain personnel : recherche de NICKNAME dans le classement ---
    gain = 0.0
    # Ex: "  25: psychoman59 (France), €31,42 (0,434%)"
    gain_pattern = re.compile(
        rf"^\s*\d+:\s*{re.escape(NICKNAME)}\s+\([^)]*\),\s*€([0-9]+[.,]?[0-9]*)",
        re.MULTILINE | re.IGNORECASE,
    )
    gain_match = gain_pattern.search(text)
    if gain_match:
        gain = float(gain_match.group(1).replace(",", "."))

    profit = gain - buy_in_total
    players = parse_player_lines(text)

    return {
        "tournament_id": tournament_id,
        "date": date_str,
        "nb_players": nb_players,
        "buy_in_total": buy_in_total,
        "dotation": dotation,
        "position": position,
        "gain": gain,
        "profit": profit,
        "players": players,
    }


def parse_player_lines(text: str) -> list[dict]:
    """Extract player rows from the tournament file text."""
    lines = text.splitlines()
    player_lines: list[str] = []
    for index, line in enumerate(lines):
        if re.match(r"^\s*\d+:\s*[^(]+\([^)]*\),", line):
            player_lines.append(line)
        elif player_lines and line.strip() == "":
            break

    players: list[dict] = []
    player_pattern = re.compile(r"^\s*\d+:\s*([^\s(]+)\s*\(([^)]+)\),\s*(.*)$")
    for line in player_lines:
        match = player_pattern.match(line)
        if not match:
            continue

        pseudo = match.group(1).strip()
        city_name = match.group(2).strip()
        status = match.group(3).strip() or None

        players.append(
            {
                "pseudo": pseudo,
                "type": status,
                "countrycity": city_name,
            }
        )

    return players


def get_or_create_countrycity(cursor: sqlite3.Cursor, name: str) -> int:
    cursor.execute(
        "INSERT OR IGNORE INTO countrycity (name) VALUES (?)",
        (name,),
    )
    cursor.execute("SELECT id FROM countrycity WHERE name = ?", (name,))
    row = cursor.fetchone()
    return row[0] if row else None


def get_tournament_row_id(cursor: sqlite3.Cursor, tournament_id: str) -> int | None:
    cursor.execute("SELECT id FROM tournaments WHERE tournament_id = ?", (tournament_id,))
    row = cursor.fetchone()
    return row[0] if row else None


def save_player(cursor: sqlite3.Cursor, player: dict) -> int:
    id_countrycity = get_or_create_countrycity(cursor, player["countrycity"])
    cursor.execute(
        "SELECT id FROM players WHERE pseudo = ?",
        (player["pseudo"],),
    )
    existing = cursor.fetchone()
    if existing:
        player_id = existing[0]
        cursor.execute(
            "UPDATE players SET type = ?, id_countrycity = ? WHERE id = ?",
            (player["type"], id_countrycity, player_id),
        )
    else:
        cursor.execute(
            "INSERT INTO players (pseudo, type, id_countrycity) VALUES (?, ?, ?)",
            (player["pseudo"], player["type"], id_countrycity),
        )
        player_id = cursor.lastrowid
    return player_id


def save_players(players: list[dict]) -> list[int]:
    if not players:
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    player_ids: list[int] = []
    for player in players:
        player_ids.append(save_player(cursor, player))
    conn.commit()
    conn.close()
    return player_ids


def save_tournament_players(tournament_id: str, player_ids: list[int]) -> None:
    if not player_ids:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    tour_id = get_tournament_row_id(cursor, tournament_id)
    if tour_id is None:
        conn.close()
        return
    for player_id in player_ids:
        cursor.execute(
            "INSERT OR IGNORE INTO tournament_players (tournament_id, player_id) VALUES (?, ?)",
            (tour_id, player_id),
        )
        cursor.execute(
            "UPDATE players SET nbTour = (SELECT COUNT(*) FROM tournament_players WHERE player_id = ?) WHERE id = ?",
            (player_id, player_id),
        )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# 4. Insertion / mise à jour en base
# ---------------------------------------------------------------------------

def upsert_tournament(data: dict) -> bool:
    """Insère ou remplace un tournoi dans la base SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    """ ON CONFLICT(tournament_id) DO UPDATE SET
                    date         = excluded.date,
                    nb_players   = excluded.nb_players,
                    buy_in_total = excluded.buy_in_total,
                    dotation     = excluded.dotation,
                    position     = excluded.position,
                    gain         = excluded.gain,
                    profit       = excluded.profit 
    """
    
    try:
        cursor.execute(
            """
            INSERT INTO tournaments
                (tournament_id, date, nb_players, buy_in_total, dotation, position, gain, profit)
            VALUES
                (:tournament_id, :date, :nb_players, :buy_in_total, :dotation, :position, :gain, :profit)
            ON CONFLICT(tournament_id) DO NOTHING  
            """,
            data,
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[ERREUR DB] {data['tournament_id']} : {e}")
        return False
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 5. Fonction principale
# ---------------------------------------------------------------------------

def run_parser(directory: str = "./dataps"):
    obj_sync_file = sync_files.sync_files()
    obj_sync_file.sync_new_tournaments(obj_sync_file.SOURCE_DIRS, obj_sync_file.DEFAULT_DEST_DIR) 
    
    """Scanne le répertoire, parse tous les TS_*.txt et alimente la BDD."""
    db_init_first = db_functions.db_functions().db_init()
    # init_db()
    obj_sync_history = sync_history_file.sync_history_file()
    obj_sync_history.read_history()
    path_dir = Path(directory)
    files = sorted(path_dir.glob("TS_*.txt"))

    if not files:
        print("Aucun fichier TS_*.txt trouvé.")
        return

    inserted = 0
    skipped = 0

    for fp in files:
        data = parse_tournament_file(fp)
        
        # data = extract_tournament_info.extract_tournament_info(fp).extract_info()
        
        if data is None:
            print(f"[SKIP] {fp.name} — format non reconnu")
            skipped += 1
            continue

        if data["date"] is None:
            print(f"[WARN] {fp.name} — date non détectée")

        if upsert_tournament(data):
            player_ids = save_players(data.get("players", []))
            save_tournament_players(data["tournament_id"], player_ids)
        profit = data["gain"] - data["buy_in_total"]
        print(
            f"[OK] #{data['tournament_id']} | "
            f"{data['date'][:10] if data['date'] else 'N/A'} | "
            f"{data['nb_players']} joueurs | "
            f"buy-in {data['buy_in_total']:.2f}€ | "
            f"dotation {data['dotation']:.2f}€ | "
            f"position {data['position']} | "
            f"gain {data['gain']:.2f}€ | "
            f"profit {profit:+.2f}€"
        )
        inserted += 1

    print(f"\n{'='*60}")
    print(f"Fichiers traités : {len(files)}")
    print(f"Insérés/Mis à jour : {inserted}")
    print(f"Ignorés : {skipped}")
    print(f"Base : {Path(DB_PATH).resolve()}")


# ---------------------------------------------------------------------------
# 6. Point d'entrée
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_parser()
