from settings import connection
from api.errors import DEFAULT_ERROR_DICT
from utils import print_debug


def user_objects_get(slug, query_args):
    desc = query_args.get('desc', False)
    desc = True if desc == 'true' else False
    since = query_args.get('since')
    limit = query_args.get('limit')
    if limit:
        limit = int(limit)
    forum_id = connection.prepare('SELECT id from forum WHERE slug = $1').first(slug)
    if not forum_id:
        error = DEFAULT_ERROR_DICT
        return error, 404
    sort_option = ['ASC', 'DESC'][desc]
    comp = ['>', '<'][desc]
    since_opt = ''

    if limit:
        limit_opt = 'LIMIT $2'
        if since:
            since_opt = 'AND usernick ' + comp + '$3'

        sql_query = '''
SELECT usr.*
FROM userforum
  JOIN "user" AS usr ON userid = usr.id
WHERE forumid = $1 {since}
ORDER BY usernick {sort} {limit}'''.format(sort=sort_option, limit=limit_opt, since=since_opt)
        users_select = connection.prepare(sql_query)

        if since:
            users = users_select(forum_id, limit, since)
        else:
            users = users_select(forum_id, limit)
    else:
        if since:
            since_opt = 'AND nickname ' + comp + '$2'

        sql_query = '''
SELECT usr.*
FROM userforum
  JOIN "user" AS usr ON userid = usr.id
WHERE forumid = $1 {since}
ORDER BY usernick {sort}'''.format(sort=sort_option, since=since_opt)
        users_select = connection.prepare(sql_query)

        if since:
            users = users_select(forum_id, since)
        else:
            users = users_select(forum_id)

    result = [{'nickname': user[1], 'about': user[2], 'email': user[3], 'fullname': user[4]} for user in users]
    return result, 200
