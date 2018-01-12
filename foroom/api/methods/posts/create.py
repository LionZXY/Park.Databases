import arrow
from postgresql.types import Array

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
            message_parents_select = connection.prepare('SELECT threadid FROM message WHERE id = ANY ($1)')
            author_select = connection.prepare('SELECT * FROM "user" WHERE nickname = ANY($1)')

            message_insert = connection.prepare('INSERT INTO message VALUES (DEFAULT, $1::TEXT::TIMESTAMP, $2::TEXT, FALSE,'
                                        ' $3::BIGINT, $4::BIGINT, $5::BIGINT, $6::BIGINT, $7::BIGINT[] || $8::BIGINT)')

            forum_select = connection.prepare('SELECT * FROM forum WHERE id = $1::BIGINT')
            forum = forum_select.first(thread[6])
            forum_slug = forum[1]
            forum_id = forum[0]

            message_parents = set()
            for item in payload:
                authors.append(item['author'])
                parent = item.get('parent')
                if parent:
                    message_parents.add(parent)

            message_parent_thread_ids = message_parents_select(list(message_parents))
            if len(message_parent_thread_ids) < len(message_parents):
                error = DEFAULT_ERROR_DICT
                return error, 409  # fake parent

            for parent_thread_id in message_parent_thread_ids:
                if parent_thread_id[0] != thread_id:
                    error = DEFAULT_ERROR_DICT
                    return error, 409  # parent from different thread

            author_records = author_select(authors)

            nickname_to_id = {}
            id_to_nickname = {}
            for author_id, author_nickname, _, _, _ in author_records:
                nickname_to_id[author_nickname] = author_id
                id_to_nickname[author_id] = author_nickname

            messages = []
            message_parent_select = connection.prepare('SELECT parenttree FROM message where message.id = $1::BIGINT')

            try:
                for item in payload:
                    parent_id = item.get('parent', None)
                    if parent_id:
                        message_parent = message_parent_select.first(parent_id)
                        messages.append(
                            (created, item['message'], nickname_to_id[item['author']], item.get('parent', None),
                             thread_id, forum_id, message_parent, parent_id))
                    else:
                        messages.append(
                            (created, item['message'], nickname_to_id[item['author']], item.get('parent', None),
                             thread_id, forum_id, Array([]), 0))
            except KeyError:
                error = DEFAULT_ERROR_DICT
                return error, 404

            message_insert.load_rows(messages)
            last_id_select = connection.prepare('select CURRVAL(\'message_id_seq\')')
            last_id = last_id_select.first()

            created = normalize_timestamp(created, json_format=True, time_to='+03:00')

            result = []
            message_count = len(messages)
            for counter in range(message_count):
                x = messages[counter]
                message = {'created': created, 'message': x[1], 'author': id_to_nickname[x[2]],
                           'id': last_id - message_count + counter + 1, 'parent': to_int(x[3]),
                           'thread': thread_id, 'forum': forum_slug}

                result.append(message)
                counter += 1

            return result, 201
    except:
        import traceback
        print(traceback.format_exc())
