import sqlite3
conn = sqlite3.connect(r'd:/IA/Softwares/IA Poker/tournaments.db')
cur = conn.cursor()
for name in ['countrycity', 'players']:
    print('TABLE', name)
    cur.execute(f"PRAGMA table_info({name});")
    print(cur.fetchall())
    cur.execute(f"PRAGMA index_list({name});")
    print('INDEXES', cur.fetchall())
    if name == 'countrycity':
        cur.execute("SELECT name, COUNT(*) FROM countrycity GROUP BY name HAVING COUNT(*) > 1")
        print('DUPES', cur.fetchall())
    if name == 'players':
        cur.execute("SELECT pseudo, COUNT(*) FROM players GROUP BY pseudo HAVING COUNT(*) > 1")
        print('DUPES', cur.fetchall())
    print()
conn.close()
