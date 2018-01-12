from settings import connection


def service_status_get():
    status = connection.prepare('''
        SELECT count(forum.id) FROM forum
        UNION ALL
        SELECT count(thread.id) FROM thread
        UNION ALL
        SELECT count("user".id) FROM "user"
        UNION ALL
        SELECT count(message.id) FROM message''')()

    resp = {
        'forum': status[0][0],
        'post': status[3][0],
        'thread': status[1][0],
        'user': status[2][0]
    }

    return resp, 200


def service_clear():
    connection.execute('TRUNCATE "user", message, thread, forum, vote CASCADE;')
    resp = {'status': 'ok'}
    return resp, 200
