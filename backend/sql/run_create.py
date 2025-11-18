import psycopg2

try:
    conn = psycopg2.connect(
        host='anytalk.com',
        port=5435,
        dbname='postgres',
        user='postgres',
        password='susoft4216!'
    )
    cur = conn.cursor()
    
    # Read SQL file
    with open(r'C:\Users\lenovo\Documents\code\jetbrain\saeum\saeum-ai-api\backend\sql\create_prompt_tables.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Execute
    cur.execute(sql)
    conn.commit()
    
    print('SUCCESS: Tables created')
    
    # Verify
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'saeum_ai_api' ORDER BY table_name")
    tables = cur.fetchall()
    print(f'\nTables ({len(tables)}):')
    for t in tables:
        print(f'  - {t[0]}')
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
