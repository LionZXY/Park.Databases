from postgresql.exceptions import UniqueError

from api.methods.helpers import increment_thread_count
from settings import connection
from utils import flush_dictionary, normalize_timestamp
from api.errors import DEFAULT_ERROR_DICT


def thread_create(slug, payload):
    author = payload.get('author')
    created = payload.get('created')
    thread_slug = payload.get('slug')
    message = payload.get('message')
    title = payload.get('title')

    try:
        with connection.xact():
            if created:
                created = normalize_timestamp(created)

            author_select = connection.prepare('SELECT * FROM "user" WHERE nickname = $1::CITEXT')
            forum_select = connection.prepare('SELECT * FROM forum WHERE slug = $1::CITEXT')
            thread_create = connection.prepare(
                'INSERT INTO thread VALUES (DEFAULT, $1::CITEXT, $2::TEXT::TIMESTAMP, '
                '$3::TEXT, $4::TEXT, $5::BIGINT, $6::BIGINT) RETURNING id')
            forum = forum_select.first(slug)
            if not forum:
                resp = DEFAULT_ERROR_DICT
                return resp, 404
            author = author_select.first(author)
            if not author:
                resp = DEFAULT_ERROR_DICT
                return resp, 404
            thread_id = thread_create.first(thread_slug, created, message, title, author[0], forum[0])

            increment_thread_count(forum[0])

            connection.prepare('INSERT INTO userforum (forumid, usernick, userid) VALUES ($1, $2::CITEXT, $3) ON CONFLICT DO NOTHING;')(forum[0], author[1], author[0])

            raw_resp = {
                'slug': thread_slug,
                'forum': forum[1],
                'message': message,
                'title': title,
                'author': author[1],
                'id': thread_id,
                'created': created
            }
            resp = flush_dictionary(raw_resp)
            return resp, 201

    except UniqueError:
        thread_select = connection.prepare('SELECT * FROM thread WHERE slug = $1::CITEXT')
        thread = thread_select.first(thread_slug)
        thread_id = thread[0]
        author_id = thread[5]
        forum_id = thread[6]
        author = connection.prepare('SELECT * FROM "user" WHERE id = $1::BIGINT').first(author_id)
        forum = connection.prepare('SELECT * FROM forum WHERE id = $1::BIGINT').first(forum_id)

        raw_resp = {
            'slug': thread[1],
            'forum': forum[1],
            'message': thread[3],
            'title': thread[4],
            'author': author[1],
            'id': thread_id,
            'created': normalize_timestamp(thread[2])
        }
        resp = flush_dictionary(raw_resp)
        return resp, 409
