import sqlite3

conn = sqlite3.connect('ganana.db')
cursor = conn.cursor()

# Get tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', tables)

# Check inventory
cursor.execute('SELECT * FROM inventory_level LIMIT 5')
inv = cursor.fetchall()
print('Inventory:', inv)

# Check adjustment logs
cursor.execute('SELECT * FROM adjustment_log LIMIT 5')
logs = cursor.fetchall()
print('Adjustment Logs:', logs)

conn.close()
