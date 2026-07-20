import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for t in tables:
    name = t[0]
    cursor.execute(f'SELECT COUNT(*) FROM [{name}]')
    count = cursor.fetchone()[0]
    print(f'{name}: {count} yozuv')
conn.close()
