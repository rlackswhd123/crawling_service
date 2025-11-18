import psycopg2

conn = psycopg2.connect(
    host='anytalk.com',
    port=5435,
    dbname='postgres',
    user='postgres',
    password='susoft4216!'
)

cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'saeum_ai_api'")
tables = [t[0] for t in cur.fetchall()]
print(f'Tables: {tables}')
cur.close()
conn.close()
