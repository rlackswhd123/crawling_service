import psycopg2

conn = psycopg2.connect(
    host='anytalk.com',
    port=5435,
    dbname='postgres',
    user='postgres',
    password='susoft4216!'
)

cur = conn.cursor()

# 스키마별 테이블 확인
cur.execute("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_schema IN ('public', 'saeum_ai_api') 
    ORDER BY table_schema, table_name
""")

tables = cur.fetchall()
print('Tables by schema:')
for schema, table in tables:
    print(f'  - {schema}.{table}')

# 시퀀스 확인
cur.execute("""
    SELECT sequence_schema, sequence_name
    FROM information_schema.sequences
    WHERE sequence_schema = 'saeum_ai_api'
""")

seqs = cur.fetchall()
print(f'\nSequences in saeum_ai_api ({len(seqs)}):')
for schema, seq in seqs:
    print(f'  - {schema}.{seq}')

cur.close()
conn.close()
