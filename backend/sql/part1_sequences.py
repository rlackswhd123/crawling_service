import psycopg2

conn = psycopg2.connect(
    host='anytalk.com', port=5435, dbname='postgres',
    user='postgres', password='susoft4216!'
)
cur = conn.cursor()

cur.execute("CREATE SEQUENCE IF NOT EXISTS saeum_ai_api.prompts_seq START 1")
conn.commit()
print('prompts_seq created')

cur.execute("CREATE SEQUENCE IF NOT EXISTS saeum_ai_api.prompt_test_results_seq START 1")
conn.commit()
print('prompt_test_results_seq created')

cur.execute("CREATE SEQUENCE IF NOT EXISTS saeum_ai_api.prompt_ratings_seq START 1")
conn.commit()
print('prompt_ratings_seq created')

cur.close()
conn.close()
print('All sequences created successfully')
