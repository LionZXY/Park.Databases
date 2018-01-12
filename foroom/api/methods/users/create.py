from postgresql.exceptions import UniqueError

from settings import connection
from utils import flush_dictionary


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


