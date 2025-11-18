import psycopg2

conn = psycopg2.connect(
    host='anytalk.com',
    port=5435,
    dbname='postgres',
    user='postgres',
    password='susoft4216!'
)

cur = conn.cursor()

# 1. 시퀀스 생성
print('Creating sequences...')
cur.execute("CREATE SEQUENCE IF NOT EXISTS saeum_ai_api.prompts_seq START 1")
cur.execute("CREATE SEQUENCE IF NOT EXISTS saeum_ai_api.prompt_test_results_seq START 1")
cur.execute("CREATE SEQUENCE IF NOT EXISTS saeum_ai_api.prompt_ratings_seq START 1")
conn.commit()
print('✓ Sequences created')

# 2. prompts 테이블
print('Creating prompts table...')
cur.execute("""
CREATE TABLE IF NOT EXISTS saeum_ai_api.prompts (
    prompt_key bigint PRIMARY KEY DEFAULT nextval('saeum_ai_api.prompts_seq'),
    prompt_kind character varying(100) NOT NULL,
    model_kind character varying(50),
    prompt_title character varying(255) NOT NULL,
    prompt_text text NOT NULL,
    prompt_desc text,
    is_default_yn smallint DEFAULT 0,
    use_count integer DEFAULT 0,
    success_count integer DEFAULT 0,
    avg_rating numeric(3,2),
    cre_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    cre_user_key bigint,
    upd_date timestamp with time zone,
    upd_user_key bigint,
    delete_yn smallint DEFAULT 0
)
""")
conn.commit()
print('✓ prompts table created')

print('Done!')
cur.close()
conn.close()
