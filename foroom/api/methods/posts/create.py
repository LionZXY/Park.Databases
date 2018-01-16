import arrow
from postgresql.types import Array
from pprint import pprint

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
        with connection.xact():
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
                   WHERE nickname = $3 :: CITEXT;''')

            messages = []

            try:
                for item in payload:
                    messages.append(
                        (created, item['message'], item['author'], thread_id, forum_id,
                         item.get('parent', 0)))
            except KeyError:
                error = DEFAULT_ERROR_DICT
                return error, 404

            try:
                message_insert_result = message_insert.load_rows(messages)
            except Exception as e:
                print("==============================")
                pprint(vars(e))
                print(e.message)
                print("==============================")
                if e.message == 'invalid_foreign_key':
                    error = DEFAULT_ERROR_DICT
                    return error, 409

            if message_insert_result is not None:
                print(message_insert_result)

            last_id_select = connection.prepare('select CURRVAL(\'message_id_seq\')')
            last_id = last_id_select.first()

            created = normalize_timestamp(created, json_format=True, time_to='+03:00')

            result = []
            message_count = len(messages)
            for counter in range(message_count):
                x = messages[counter]
                message = {'created': created, 'message': x[1], 'author': x[2],
                           'id': last_id - message_count + counter + 1, 'parent': to_int(x[5]),
                           'thread': thread_id, 'forum': forum_slug}

                result.append(message)
                counter += 1

            return result, 201
    except:
        import traceback
        print(traceback.format_exc())
