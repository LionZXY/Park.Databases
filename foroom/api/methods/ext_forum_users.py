from settings import connection
from api.errors import DEFAULT_ERROR_DICT
from utils import print_debug


def forum_users_get(slug, query_args):
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

    if limit:
        limit_opt = 'LIMIT $2'
        if since:
            since_opt = 'AND "user".nickname ' + comp + '$3'
            sql_query = '''
                	SELECT nickname, about, email, fullname, lower(nickname) as sorting from thread 
                	JOIN "user" on "user".id = thread.authorid 
                	WHERE thread.forumid = $1
                	{since}
                	UNION
                	SELECT nickname, about, email, fullname, lower(nickname) as sorting from message 
                	JOIN "user" on "user".id = message.authorid 
                	WHERE message.forumid = $1
                	{since}
                	ORDER BY sorting {sort} {limit}
                	'''.format(sort=sort_option, limit=limit_opt, since=since_opt)
            users_select = connection.prepare(sql_query)
            users = users_select(forum_id, limit, since)
        else:
            sql_query = '''
                        SELECT nickname, about, email, fullname, lower(nickname) as sorting from thread 
                        JOIN "user" on "user".id = thread.authorid 
                        WHERE thread.forumid = $1
                        UNION
                        SELECT nickname, about, email, fullname, lower(nickname) as sorting from message 
                        JOIN "user" on "user".id = message.authorid 
                        WHERE message.forumid = $1
                        ORDER BY sorting {sort} {limit}
                        '''.format(sort=sort_option, limit=limit_opt)
            users_select = connection.prepare(sql_query)
            users = users_select(forum_id, limit)
    else:
        if since:
            since_opt = 'AND "user".nickname ' + comp + '$2'
            sql_query = '''
                        SELECT nickname, about, email, fullname, lower(nickname) as sorting from thread 
                        JOIN "user" on "user".id = thread.authorid 
                        WHERE thread.forumid = $1
                        {since}
                        UNION
                        SELECT nickname, about, email, fullname, lower(nickname) as sorting from message 
                        JOIN "user" on "user".id = message.authorid 
                        WHERE message.forumid = $1
                        {since}
                        ORDER BY sorting {sort}
                        '''.format(sort=sort_option, since=since_opt)
            users_select = connection.prepare(sql_query)
            users = users_select(forum_id, since)
        else:
            sql_query = '''
                        SELECT nickname, about, email, fullname, lower(nickname) as sorting from thread 
                        JOIN "user" on "user".id = thread.authorid 
                        WHERE thread.forumid = $1
                        UNION
                        SELECT nickname, about, email, fullname, lower(nickname) as sorting from message 
                        JOIN "user" on "user".id = message.authorid 
                        WHERE message.forumid = $1
                        ORDER BY sorting {sort}
                        '''.format(sort=sort_option)
            users_select = connection.prepare(sql_query)
            users = users_select(forum_id)

    result = [{'nickname': user[0], 'about': user[1], 'email': user[2], 'fullname': user[3]} for user in users]
    return result, 200