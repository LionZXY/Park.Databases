from settings import connection
from utils import normalize_timestamp, parse_slug_or_id
import api
from api.errors import DEFAULT_ERROR_DICT


def thread_details_get(slug_or_id):
    thread_id = None
    thread_slug = None
    try:
        thread_id = int(slug_or_id)
    except ValueError:
        thread_slug = slug_or_id
    # try:
    if thread_id:
        thread = api.methods.thread_select_by_id.first(thread_id)
    else:
        thread = api.methods.thread_select_by_slug.first(thread_slug)
    if not thread:
        error = DEFAULT_ERROR_DICT
        return error, 404

    thread_id, thread_slug, thread_created_on, thread_message, \
    thread_title, thread_author_id, forum_id \
        = thread

    votes = connection.prepare('''SELECT sum(voice) FROM thread 
                JOIN vote ON vote.threadid = thread.id WHERE thread.id = $1''').first(thread_id)

    forum_slug = api.methods.forum_select_by_id.first(forum_id)[1]

    author = api.methods.user_select_by_id.first(thread_author_id)[1]
    # print('--------------------> trying to set +03:00')
    resp = {
        'slug': thread_slug,
        'forum': forum_slug,
        'message': thread_message,
        'title': thread_title,
        'author': author,
        'id': thread_id,
        'created': normalize_timestamp(thread_created_on, time_to='+03:00', database_format=True),
        'votes': votes
    }
    return resp, 200


def thread_details_update(slug_or_id, payload):
    thread_slug, thread_id = parse_slug_or_id(slug_or_id)
    message = payload.get('message')
    title = payload.get('title')

    with connection.xact():
        thread_update = connection.prepare('''UPDATE thread SET message = coalesce($2, message), title = coalesce($3, title) WHERE {cond}
            RETURNING id, slug, created_on, message, title, authorid, forumid'''.format(
            cond='id = $1' if thread_id else 'slug = $1'))

        if thread_id:
            thread = thread_update.first(thread_id, message, title)
        else:
            thread = thread_update.first(thread_slug, message, title)

        if not thread:
            error = DEFAULT_ERROR_DICT
            return error, 404
        thread_id, thread_slug, thread_created_on, thread_message, \
        thread_title, thread_author_id, forum_id \
            = thread

        author = api.methods.user_select_by_id.first(thread_author_id)[1]
        forum_slug = api.methods.forum_select_by_id.first(forum_id)[1]

    resp = {
        'slug': thread_slug,
        'forum': forum_slug,
        'message': thread_message,
        'title': thread_title,
        'author': author,
        'id': thread_id,
        'created': normalize_timestamp(thread_created_on)
    }
    return resp, 200
