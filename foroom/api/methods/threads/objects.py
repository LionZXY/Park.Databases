from settings import connection
from utils import normalize_timestamp, flush_dictionary
from api.errors import DEFAULT_ERROR_DICT


def thread_objects_get(slug, query_args):
    limit = query_args.get('limit')
    desc = query_args.get('desc', False)
    desc = True if desc == 'true' else False

    since = query_args.get('since')
    sort_option = ['ASC', 'DESC'][1 if desc else 0]
    since_cond = ''
    if since is not None:
        # since = normalize_timestamp(since.decode('utf-8'))
        since = normalize_timestamp(since)
        since_cond = ' AND created_on ' + ['>=', '<='][1 if desc else 0] + '\'' + str(since) + '\''

    forum_select = connection.prepare('SELECT * FROM forum WHERE slug = $1::CITEXT')
    forum = forum_select.first(slug)

    if not forum:
        resp = DEFAULT_ERROR_DICT
        return resp, 404
    thread_select = connection.prepare('SELECT t.id, slug, created_on, message, title, nickname'
                               ' FROM thread as t'
                               ' JOIN "user" as u ON t.authorid = u.id  WHERE t.forumid = $1::BIGINT'
                               + since_cond +
                               ' ORDER BY created_on ' + sort_option +
                               ' LIMIT $2')
    threads = []

    for id, slug, created, message, title, nickname in thread_select(forum[0], int(limit) if limit else None):
        thread = {
            'id': id,
            'slug': slug,
            'created': normalize_timestamp(created),
            'message': message,
            'title': title,
            'author': nickname,
            'forum': forum[1]
        }

        threads.append(flush_dictionary(thread))
    return threads, 200
