import sqlite3

conn = sqlite3.connect(r'd:/IA/Softwares/IA Poker/tournaments.db')
cur = conn.cursor()
try:
    cur.execute('ALTER TABLE players DROP COLUMN id_hand')
    print('dropped via ALTER TABLE')
except sqlite3.OperationalError as e:
    print('ALTER TABLE failed:', e)
    print('Recreating players table without id_hand...')
    cur.execute('PRAGMA foreign_keys = OFF')
    cur.execute('BEGIN TRANSACTION')
    cur.execute('CREATE TABLE IF NOT EXISTS players_new (id INTEGER PRIMARY KEY, pseudo TEXT NOT NULL, type TEXT, id_countrycity INTEGER, FOREIGN KEY(id_countrycity) REFERENCES countrycity(id))')
    cur.execute('INSERT INTO players_new (id, pseudo, type, id_countrycity) SELECT id, pseudo, type, id_countrycity FROM players')
    cur.execute('DROP TABLE players')
    cur.execute('ALTER TABLE players_new RENAME TO players')
    cur.execute('PRAGMA foreign_keys = ON')
    print('recreated players table')
conn.commit()
conn.close()
