from settings import connection
from utils import normalize_timestamp, parse_slug_or_id, to_int, print_debug
from api.errors import DEFAULT_ERROR_DICT


def post_objects_get(slug_or_id, query_args):
    thread_slug, thread_id = parse_slug_or_id(slug_or_id)
    sort = query_args.get('sort')
    since = query_args.get('since')
    if since is not None:
        since = int(since)

    desc = query_args.get('desc', False)
    desc = True if desc == 'true' else False
    if desc:
        sort_option = 'DESC'
    else:
        sort_option = 'ASC'

    limit = int(query_args.get('limit'))

    comp = ['>', '<'][1 if desc else 0]
    if since:
        since_cond_message = ' AND message.id ' + ['>', '<'][1 if desc else 0] + ' $3::BIGINT'
        since_cond_m = ' WHERE m.id ' + ['>', '<'][1 if desc else 0] + ' $3::BIGINT'
        since_cond_tree = 'WHERE m.parenttree || m.id ' + comp + ' (SELECT parenttree || id FROM message WHERE id = $3::BIGINT)'  # AND (message.parenttree[2] ' + ['>', '<'][desc] + ' $3::BIGINT OR message.parenttree[2] IS NULL) '
    else:
        since_cond_tree = since_cond_message = since_cond_m = ''
    select_fields = 'SELECT m.id, m.created_on, m.message, m.threadid, m.parentid, "user".nickname, forum.slug'
    inner_select_fields = '''SELECT message.id, message.created_on, message.threadid, message.message,
                             message.parentid, message.authorid, message.forumid'''
    inner_select_fields_tree = inner_select_fields + ', message.parenttree'

    with connection.xact():
        messages = []
        if not thread_id:
            thread_id = connection.prepare('SELECT id FROM thread WHERE slug = $1').first(thread_slug)
        else:
            thread_id = connection.prepare('SELECT id FROM thread WHERE id = $1').first(thread_id)
        if not thread_id:
            error = DEFAULT_ERROR_DICT
            return error, 404
        if sort == 'flat' or sort is None:
            if thread_slug:
                message_select = connection.prepare('''
                    {select_fields}
                     FROM (
                         {select_inner}
                         FROM message JOIN thread ON message.threadid = thread.id 
                         WHERE thread.slug = $1 {since} ORDER BY message.id {sort} LIMIT $2
                     ) as m
                     JOIN "user" ON "user".id = m.authorid
                     JOIN forum ON m.forumid = forum.id
                     ORDER BY m.id  {sort}'''.format(sort=sort_option, since=since_cond_message,
                                                     select_fields=select_fields,
                                                     select_inner=inner_select_fields))
                if since:
                    messages = message_select(thread_slug, limit, since)
                else:
                    messages = message_select(thread_slug, limit)
            else:
                message_select = connection.prepare('''
                    {select_fields}
                     FROM (
                        {select_inner}
                        FROM message WHERE message.threadid = $1 {since} ORDER BY message.id {sort} LIMIT $2
                     ) as m
                     JOIN "user" ON "user".id = m.authorid
                     JOIN forum ON m.forumid = forum.id
                     ORDER BY m.id {sort}'''.format(sort=sort_option, since=since_cond_message,
                                                    select_fields=select_fields, select_inner=inner_select_fields))
                if since:
                    messages = message_select(thread_id, limit, since)
                else:
                    messages = message_select(thread_id, limit)
        elif sort == 'tree':
            if thread_slug:
                message_select = connection.prepare('''
                        {select_fields}
                         FROM (
                             {select_inner} 
                             FROM message JOIN thread ON message.threadid = thread.id 
                             WHERE thread.slug = $1 ORDER BY message.parenttree || message.id {sort}
                         ) as m
                         JOIN "user" ON "user".id = m.authorid
                         JOIN forum ON m.forumid = forum.id
                         {since}
                         ORDER BY m.parenttree || m.id {sort} LIMIT $2'''.format(sort=sort_option,
                                                                                 since=since_cond_tree,
                                                                                 select_fields=select_fields,
                                                                                 select_inner=inner_select_fields_tree))
                if since:
                    messages = message_select(thread_slug, limit, since)
                else:
                    messages = message_select(thread_slug, limit)
            else:
                message_select = connection.prepare('''
                        {select_fields}
                         FROM (
                             {select_inner}
                             FROM message
                             WHERE message.threadid = $1 ORDER BY message.parenttree || message.id {sort}
                         ) as m
                         JOIN "user" ON "user".id = m.authorid
                         JOIN forum ON m.forumid = forum.id
                         {since}
                         ORDER BY m.parenttree || m.id {sort} LIMIT $2'''.format(sort=sort_option,
                                                                                 since=since_cond_tree,
                                                                                 select_fields=select_fields,
                                                                                 select_inner=inner_select_fields_tree))
                if since:
                    messages = message_select(thread_id, limit, since)
                else:
                    messages = message_select(thread_id, limit)
        elif sort == 'parent_tree':
            if since:
                message_select = connection.prepare('''
                    {select_fields}
                    FROM (
                        SELECT * FROM message
                        WHERE message.threadid = $1 AND (message.parenttree)[1] in (
                            SELECT
                                m1.id
                                 FROM message m1
                                 WHERE m1.parentid = 0 AND m1.threadid = $1 AND m1.parenttree {comp} (
                                         SELECT m2.parenttree
                                         FROM message m2
                                         WHERE m2.id = $3
                                 )
                                 ORDER BY m1.parenttree {sort} LIMIT $2
                            )
                    ) as m
                    JOIN "user" ON "user".id = m.authorid
                    JOIN forum ON m.forumid = forum.id
                    ORDER BY m.parenttree {sort},
                    m.threadid {sort}'''.format(sort=sort_option, comp=comp, since=since_cond_message,
                                                select_fields=select_fields, select_inner=inner_select_fields_tree))
                messages = message_select(thread_id, limit, since)
            else:
                message_select = connection.prepare('''
                    {select_fields}
                    FROM (
                        SELECT * FROM message
                        WHERE message.threadid = $1 AND message.parenttree [1] in (
                            SELECT
                                m1.id 
                                 FROM message m1
                                 WHERE m1.parentid = 0 AND m1.threadid = $1
                                 ORDER BY m1.parenttree {sort} LIMIT $2
                            )
                    ) as m
                    JOIN "user" ON "user".id = m.authorid
                    JOIN forum ON m.forumid = forum.id
                    ORDER BY m.parenttree {sort},
                    m.threadid {sort}'''.format(sort=sort_option, since=since_cond_message, select_fields=select_fields,
                                                select_inner=inner_select_fields_tree))
                messages = message_select(thread_id, limit)

    result = []
    for x in messages:
        message = {
            'id': x[0],
            'created': normalize_timestamp(x[1], json_format=True),
            'message': x[2],
            'thread': x[3],
            'parent': to_int(x[4]),
            'author': x[5],
            'forum': x[6]
        }
        result.append(message)
    return result, 200
