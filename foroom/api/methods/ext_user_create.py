from postgresql.exceptions import UniqueError

from settings import connection
from utils import flush_dictionary

# def api_user_create_simple(nickname, params=None):
#     prep_insert_user = connection.prepare('INSERT INTO "user" VALUES (DEFAULT, $1::citext, $2::citext, $3::citext, $4::citext)')
#     prep_insert_user(nickname, params.get('about'), params.get('email'), params.get('fullname'))
#
#     return {'nickname': nickname}.update(params), 201


def _api_user_create_simple(nickname, params=None):
    # prep_insert_user = connection.prepare('INSERT INTO "user" VALUES (DEFAULT, $1::citext, $2::citext, $3::citext, $4::citext)')
    # prep_insert_user(nickname, params.get('about'), params.get('email'), params.get('fullname'))

    cursor = connection.cursor()
    # cursor.execute('INSERT INTO "user" VALUES (DEFAULT, $1::citext, $2::citext, $3::citext, $4::citext)',
    #                (nickname, params.get('about'), params.get('email'), params.get('fullname')))
    cursor.execute('INSERT INTO "user" VALUES (DEFAULT, %s::citext, %s::citext, %s::citext, %s::citext)',
                   (nickname, params.get('about'), params.get('email'), params.get('fullname')))

    payload = dict(params)
    payload['nickname'] = nickname
    return payload, 201


def _user_create(nickname, params=None):
    prep_insert_user = connection.prepare('INSERT INTO "user" VALUES (DEFAULT, $1::citext, $2::citext, $3::citext, $4::citext)')
    prep_insert_user(nickname, params.get('about'), params.get('email'), params.get('fullname'))

    payload = dict(params)
    payload['nickname'] = nickname
    return payload, 201


def user_create(nickname, payload=None):
    about = payload.get('about')
    email = payload.get('email')
    fullname = payload.get('fullname')
    try:
        with connection.xact():
            user_insert = connection.prepare(
                'INSERT INTO "user" VALUES (DEFAULT, $1::citext, $2::citext, $3::citext, $4::citext)')
            user_insert(nickname, about, email, fullname)
    except UniqueError:
        user_select = connection.prepare('SELECT * FROM "user" WHERE nickname = $1::citext OR email = $2::citext')
        conflict_list = []
        for _, ex_nickname, ex_about, ex_email, ex_fullname in user_select(nickname, email):
            conflict_list.append(flush_dictionary({'nickname': ex_nickname, 'about': ex_about, 'email': ex_email,
                                             'fullname': ex_fullname}))
        return conflict_list, 409

    result = flush_dictionary({'nickname': nickname, 'about': about, 'email': email, 'fullname': fullname})
    return result, 201


