import sqlite3
DB_PASS = "tournaments.db"

class db_functions:
    
    def __init__(self):
         self.DB_PASS = DB_PASS


    def db_init(self) -> None:
        """Crée les tables SQLite nécessaires et migre la table tournaments si besoin."""
        conn = sqlite3.connect(self.DB_PASS)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tournaments (
                id            INTEGER PRIMARY KEY,
                tournament_id TEXT    UNIQUE NOT NULL,
                date          TEXT    NOT NULL,
                nb_players    INTEGER NOT NULL,
                buy_in_total  REAL    NOT NULL,
                dotation      REAL    NOT NULL,
                position      INTEGER,
                gain          REAL    DEFAULT 0,
                profit        REAL    DEFAULT 0
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS countrycity (
                id   INTEGER PRIMARY KEY,
                name TEXT    UNIQUE NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                id             INTEGER PRIMARY KEY,
                pseudo         TEXT    NOT NULL UNIQUE,
                type           TEXT,
                id_countrycity INTEGER,
                nbTour         INTEGER DEFAULT 0,
                FOREIGN KEY(id_countrycity) REFERENCES countrycity(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tournament_players (
                id            INTEGER PRIMARY KEY,
                tournament_id INTEGER NOT NULL,
                player_id     INTEGER NOT NULL,
                UNIQUE(tournament_id, player_id),
                FOREIGN KEY(tournament_id) REFERENCES tournaments(id),
                FOREIGN KEY(player_id) REFERENCES players(id)
            )
            """
        )

        cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tournaments_not_stored (
                    id            INTEGER PRIMARY KEY,
                    tournament_id TEXT    UNIQUE NOT NULL,
                    date          TEXT    NOT NULL,
                    nb_players    INTEGER NOT NULL,
                    buy_in_total  REAL    NOT NULL,
                    dotation      REAL    NOT NULL,
                    position      INTEGER,
                    gain          REAL    DEFAULT 0,
                    profit        REAL    DEFAULT 0
                )
                """
            )


        # Migration : ajouter les colonnes gain et profit si la table existait avant
        cursor.execute("PRAGMA table_info(tournaments)")
        columns = [row[1] for row in cursor.fetchall()]
        if "gain" not in columns:
            cursor.execute("ALTER TABLE tournaments ADD COLUMN gain REAL DEFAULT 0")
        if "profit" not in columns:
            cursor.execute("ALTER TABLE tournaments ADD COLUMN profit REAL DEFAULT 0")
        cursor.execute("PRAGMA table_info(players)")
        player_columns = [row[1] for row in cursor.fetchall()]
        if "nbTour" not in player_columns:
            cursor.execute("ALTER TABLE players ADD COLUMN nbTour INTEGER DEFAULT 0")
        conn.commit()
        conn.close()

    def get_or_create_countrycity(cursor: sqlite3.Cursor, name:str) -> int:
        cursor.execute(
            "INSERT OR IGNORE INTO countrycity (name) VALUES (?)",
            (name,),
        )
        cursor.execute("SELECT id FROM countrycity WHERE name = ?", (name,))
        row = cursor.fetchone()
        return row[0] if row else None

    