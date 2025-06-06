import sqlite3

conn = sqlite3.connect("bueiros_data.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM leituras")
qtd = cursor.fetchone()[0]

print(f"Total de leituras armazenadas: {qtd}")
conn.close()
