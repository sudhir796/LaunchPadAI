import sqlite3

conn = sqlite3.connect('sql_app.db')
cur = conn.cursor()
cur.execute("SELECT agent_name, status, error_message FROM agent_outputs WHERE agent_name='business_model'")
for row in cur.fetchall():
    print(row)
conn.close()