import sqlite3

connection = sqlite3.connect('searchesDB.db')
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE searches (
        search_id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT,
        timestamp TIMESTAMP
    )
""")

connection.commit()
connection.close()
