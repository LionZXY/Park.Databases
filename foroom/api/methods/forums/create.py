from settings import connection
from api.errors import DEFAULT_ERROR_DICT


def forum_create(payload):
    slug = payload.get('slug')
    title = payload.get('title')
    user = payload.get('user')

    try:
        with connection.xact():
            user_select = connection.prepare('SELECT * FROM "user" WHERE nickname = $1::CITEXT')
            forum_insert = connection.prepare(
                'INSERT INTO forum VALUES (DEFAULT, $1::CITEXT, $2::TEXT, $3::BIGINT)')

            user_record = user_select.first(user)
            if not user_record:
                resp = DEFAULT_ERROR_DICT
                return resp, 404
            user_id = user_record[0]

            forum_insert(slug, title, user_id)

            resp = {'slug': slug, 'user': user_record[1], 'title': title}
            return resp, 201
    except:
        forum_select = connection.prepare('SELECT * FROM forum WHERE slug = $1::CITEXT')
        forum = forum_select.first(slug)

        if forum:
            user_select = connection.prepare('SELECT * FROM "user" WHERE id = $1::BIGINT')
            user = user_select.first(forum[3])
            username = user[1]
            resp = {'slug': forum[1], 'user': username, 'title': forum[2]}
            return resp, 409
