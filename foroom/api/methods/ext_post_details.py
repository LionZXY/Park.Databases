from settings import connection
from api.errors import DEFAULT_ERROR_DICT
from utils import normalize_timestamp, flush_dictionary, print_debug


def post_details_get(post_id, query_args):
    post_id = int(post_id)
    related = query_args.get('related')
    # print(related)

    related_items = {
        'user': False,
        'thread': False,
        'forum': False
    }

    if related:
        related = related.split(',')
        for item in related:
            if item in ['user', 'thread', 'forum']:
                related_items[item] = True
                print(item)

    message_fields_len = 6

    message_select = connection.prepare('''
        SELECT m.created_on, m.message, "user".nickname, m.threadid, forum.slug, isedited 
        {thread_fields}
        {forum_fields}
        {user_fields}
        FROM
        (SELECT authorid, threadid, forumid, parentid, created_on, message, isedited FROM message
        WHERE id = $1) as m
        JOIN "user" ON "user".id = m.authorid
        JOIN forum ON m.forumid = forum.id
        {join_thread}
        {join_forum_author}'''.format(
        join_thread='JOIN thread on m.threadid = thread.id '
                    'JOIN "user" AS thread_author ON thread_author.id = thread.authorid' if related_items[
            'thread'] else '',
        thread_fields=', thread.id, thread.slug, thread.created_on, '
                      'thread.message, thread.title, thread_author.nickname' if related_items['thread'] else '',
        join_forum_author='JOIN "user" AS forum_author ON forum_author.id = forum.userid' if related_items[
            'forum'] else '',
        forum_fields=', forum.id, forum.title, forum_author.nickname' if related_items['forum'] else '',
        user_fields=', "user".about, "user".email, "user".fullname' if related_items['user'] else ''))

    message = message_select.first(post_id)
    if not message:
        error = DEFAULT_ERROR_DICT
        return error, 404

    if related_items['thread']:
        thread_offset = message_fields_len

        thread = {
            'id': message[thread_offset],
            'slug': message[thread_offset + 1],
            'created': normalize_timestamp(message[thread_offset + 2]),
            'message': message[thread_offset + 3],
            'title': message[thread_offset + 4],
            'author': message[thread_offset + 5],
            'forum': message[4]
        }

        thread_fields_len = 6
    else:
        thread = None
        thread_fields_len = 0

    if related_items['forum']:
        forum_offset = message_fields_len + thread_fields_len
        forum_fields_len = 3

        forum = {
            'id': message[forum_offset],
            'slug': message[4],
            'title': message[forum_offset + 1],
            'user': message[forum_offset + 2]
        }

        # Optimization zone
        forum['posts'] = connection.prepare('SELECT COUNT(id) FROM message WHERE forumid = $1').first(forum['id'])
        forum['threads'] = connection.prepare('SELECT COUNT(id) FROM thread WHERE forumid = $1').first(forum['id'])
    else:
        forum = None
        forum_fields_len = 0

    if related_items['user']:
        user_offset = message_fields_len + forum_fields_len + thread_fields_len

        user = {
            'nickname': message[2],
            'about': message[user_offset],
            'email': message[user_offset + 1],
            'fullname': message[user_offset + 2]
        }
    else:
        user = None


    post = {
        'id': post_id,
        'created': normalize_timestamp(message[0], time_to='+03:00'),
        'message': message[1],
        'author': message[2],
        'thread': message[3],
        'forum': message[4],
        'isEdited': message[5]
    }

    resp = {
        'post': post,
        'thread': thread,
        'forum': forum,
        'author': user
    }

    return flush_dictionary(resp), 200


def post_details_update(post_id, payload):
    new_message = payload.get('message')
    post_id = int(post_id)
    message_update = connection.prepare('''
                WITH updated AS (
                    UPDATE message SET message = $2, isedited = sub.isedited OR sub.message IS DISTINCT FROM $2
                    FROM (
                        SELECT * FROM message WHERE id = $1 FOR UPDATE
                    ) as sub
                    JOIN "user" ON sub.authorid = "user".id
                    JOIN forum ON sub.forumid = forum.id
                    RETURNING sub.authorid, sub.threadid, sub.forumid, 
                    sub.created_on, message.message, message.isedited, slug, nickname
                )
                SELECT created_on, message, nickname, threadid, slug, isedited FROM updated''')
    # Consider returning less  {remove thread} (Optimisation)
    # Consider using a pre-update trigger to determine isedited and prevent needless message updates (Optimisation)

    if new_message:
        message = message_update.first(post_id, new_message)
    else:
        message = connection.prepare('''
                    SELECT m.created_on, m.message, "user".nickname, m.threadid, forum.slug, isedited FROM (
                        SELECT created_on, message, authorid, threadid, forumid, isedited
                        FROM message WHERE id = $1
                    ) as m
                    JOIN "user" ON m.authorid = "user".id
                    JOIN forum ON m.forumid = forum.id''').first(post_id)

    if not message:
        error = DEFAULT_ERROR_DICT
        return error, 404
    # Consider returning less  {remove thread} (Optimisation)

    resp = {
        'id': post_id,
        'created': normalize_timestamp(message[0], time_to='+03:00'),
        'message': message[1],
        'author': message[2],
        'thread': message[3],
        'forum': message[4],
        'isEdited': message[5]
    }

    return resp, 200
