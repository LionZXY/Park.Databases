import arrow
from postgresql.types import Array
from pprint import pprint

from api.methods.NotFoundException import NotFoundException
from settings import connection
from utils import normalize_timestamp, to_int
from api.errors import DEFAULT_ERROR_DICT


def post_create(slug_or_id, payload):
    thread_id = None
    slug = None
    try:
        thread_id = int(slug_or_id)
    except:
        slug = slug_or_id
    authors = []

    created = normalize_timestamp(arrow.Arrow.utcnow())
    try:
        with connection.xact() as xact:
            # Оставить
            if thread_id is not None:
                thread_select = connection.prepare('SELECT * FROM thread WHERE id = $1::BIGINT')
                thread = thread_select.first(thread_id)
            else:
                thread_select = connection.prepare('SELECT * FROM thread WHERE slug = $1::CITEXT')
                thread = thread_select.first(slug)
            if not thread:
                error = DEFAULT_ERROR_DICT
                return error, 404
            if not payload:
                return [], 201

            thread_id = thread[0]

            forum_select = connection.prepare('SELECT id, slug FROM forum WHERE id = $1::BIGINT')
            forum = forum_select.first(thread[6])
            forum_slug = forum[1]
            forum_id = forum[0]

            # Оставить

            message_insert = connection.prepare(
                '''INSERT INTO message (created_on, "message", authorid, threadid, forumid, parentid)
                    SELECT
                      $1 :: TEXT :: TIMESTAMP,
                      $2 :: TEXT,
                      usr.id,
                      $4 :: BIGINT,
                      $5 :: BIGINT,
                      $6 :: BIGINT
                    FROM "user" AS usr
                   WHERE nickname = $3 :: CITEXT RETURNING id;''')

            result = []
            created_str = normalize_timestamp(created, json_format=True, time_to='+03:00')

            try:
                for item in payload:
                    id = message_insert(created, item['message'], item['author'], thread_id, forum_id,
                                        item.get('parent', 0))
                    if len(id) != 1:
                        xact.rollback()
                        raise NotFoundException
                    message = {'created': created_str, 'message': item['message'], 'author': item['author'],
                               'id': id[0][0], 'parent': to_int(item.get('parent', 0)),
                               'thread': thread_id, 'forum': forum_slug}
                    result.append(message)
            except KeyError:
                error = DEFAULT_ERROR_DICT
                return error, 404

            connection.prepare('''
UPDATE forum
SET posts_count = posts_count + $1
WHERE id = $2;''')(len(payload), forum_id)

            return result, 201
    except NotFoundException:
        return DEFAULT_ERROR_DICT, 404
    except Exception as e:
        if e.message == 'invalid_foreign_key':
            error = DEFAULT_ERROR_DICT
            return error, 409
        import traceback
        print(traceback.format_exc())
