from settings import connection


user_select_by_id = connection.prepare('SELECT * FROM "user" WHERE id = $1::BIGINT')
user_select_by_nickname = connection.prepare('SELECT * FROM "user" WHERE nickname = $1::CITEXT')

forum_select_by_id = connection.prepare('SELECT * FROM forum WHERE id = $1::BIGINT')

thread_select_by_id = connection.prepare('SELECT * FROM thread WHERE id = $1::BIGINT')
thread_select_by_slug = connection.prepare('SELECT * FROM thread WHERE slug = $1::CITEXT')

increment_thread_count = connection.prepare('''
UPDATE forum
SET threads_count = threads_count + 1
WHERE id = $1;''')
