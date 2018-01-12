from settings import connection
from api.errors import DEFAULT_ERROR_DICT


def forum_details_get(slug):
    forum_select = connection.prepare('SELECT * FROM forum WHERE slug = $1::CITEXT')
    forum = forum_select.first(slug)

    if forum:
        user_select = connection.prepare('SELECT * FROM "user" WHERE id = $1::BIGINT')
        user = user_select.first(forum[3])
        post_count = connection.prepare('SELECT COUNT(id) FROM message WHERE forumid = $1').first(forum[0])
        thread_count = connection.prepare('SELECT COUNT(id) FROM thread WHERE forumid = $1').first(forum[0])
        username = user[1]
        resp = {'slug': forum[1], 'user': username, 'title': forum[2], 'posts': post_count, 'threads': thread_count}
        return resp, 200
    resp = DEFAULT_ERROR_DICT
    return resp, 404
