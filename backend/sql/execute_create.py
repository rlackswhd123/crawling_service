import psycopg2

conn = psycopg2.connect(
    host='anytalk.com',
    port=5435,
    dbname='postgres',
    user='postgres',
    password='susoft4216!'
)

cur = conn.cursor()

# SQL 파일 읽기
with open('C:/Users/lenovo/Documents/code/jetbrain/saeum/saeum-ai-api/backend/sql/create_prompt_tables.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

try:
    cur.execute(sql)
    conn.commit()
    print('✓ Tables created successfully in saeum_ai_api schema')
except Exception as e:
    print(f'✗ Error: {e}')
    conn.rollback()

# 생성 확인
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'saeum_ai_api' 
    ORDER BY table_name
""")

tables = cur.fetchall()
print(f'\nCreated tables ({len(tables)}):')
for table in tables:
    print(f'  - saeum_ai_api.{table[0]}')

# 시퀀스 확인
cur.execute("""
    SELECT sequence_name
    FROM information_schema.sequences
    WHERE sequence_schema = 'saeum_ai_api'
""")

seqs = cur.fetchall()
print(f'\nCreated sequences ({len(seqs)}):')
for seq in seqs:
    print(f'  - saeum_ai_api.{seq[0]}')

cur.close()
conn.close()
