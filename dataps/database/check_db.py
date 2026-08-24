import sqlite3
conn = sqlite3.connect('tournaments.db')
cur = conn.cursor()
cur.execute('SELECT * FROM tournaments')
for row in cur.fetchall():
    print(row)
conn.close()
