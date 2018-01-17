from settings import connection
from utils import parse_slug_or_id, normalize_timestamp

import api
from api.errors import DEFAULT_ERROR_DICT


def thread_vote(slug_or_id, payload):
    nickname = payload.get('nickname')
    new_voice = payload.get('voice')

    thread_slug, thread_id = parse_slug_or_id(slug_or_id)
    try:
        with connection.xact():
            if thread_id:
                thread = api.methods.thread_select_by_id.first(thread_id)
            else:
                thread = api.methods.thread_select_by_slug.first(thread_slug)
            if not thread:
                error = DEFAULT_ERROR_DICT
                return error, 404
            thread_id, thread_slug, thread_created_on, thread_message, \
            thread_title, thread_author_id, forum_id, voice \
                = thread
            forum_slug = api.methods.forum_select_by_id.first(forum_id)[1]
            # thread_slug = thread[1]
            thread_created_on = normalize_timestamp(thread_created_on)
            # thread_title = thread[3]
            author = api.methods.user_select_by_id.first(thread_author_id)[1]

            vote_insert = connection.prepare('''
            INSERT INTO vote (voice, usernick, threadid)
            VALUES ($1 :: INTEGER, $2 :: CITEXT, $3 :: BIGINT)
            ON CONFLICT ON CONSTRAINT unique_vote
              DO UPDATE SET voice = $1;''')
            vote_insert(new_voice, nickname, thread_id)

            thread_votes_sum_select = connection.prepare('SELECT sum(voice) FROM vote WHERE threadid = $1::BIGINT')
            thread_votes_sum = thread_votes_sum_select.first(thread_id)

            resp = {
                'message': thread_message,
                'title': thread_title,
                'author': author,
                'created': thread_created_on,
                'id': thread_id,
                'slug': thread_slug,
                'votes': thread_votes_sum,
                'forum': forum_slug
            }
            return resp, 200
    except Exception as e:
        if e.code == '23503':
            return DEFAULT_ERROR_DICT, 404
        import traceback
        print(traceback.format_exc())
