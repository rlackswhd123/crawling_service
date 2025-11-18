import psycopg2
import sys

try:
    print('Connecting to DB...')
    conn = psycopg2.connect(
        host='anytalk.com',
        port=5435,
        dbname='postgres',
        user='postgres',
        password='susoft4216!'
    )
    print('Connected!')
    
    cur = conn.cursor()
    
    print('Creating sequence...')
    cur.execute("CREATE SEQUENCE IF NOT EXISTS saeum_ai_api.test_seq START 1")
    conn.commit()
    print('Sequence created!')
    
    print('Creating table...')
    cur.execute("""
        CREATE TABLE IF NOT EXISTS saeum_ai_api.test_table (
            id bigint PRIMARY KEY DEFAULT nextval('saeum_ai_api.test_seq'),
            name text
        )
    """)
    conn.commit()
    print('Table created!')
    
    # Verify
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'saeum_ai_api'")
    tables = cur.fetchall()
    print(f'\nTables in saeum_ai_api: {[t[0] for t in tables]}')
    
    cur.close()
    conn.close()
    print('\nSUCCESS')
    
except Exception as e:
    print(f'\nERROR: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
