from settings import connection
from utils import flush_dictionary
from api.errors import DEFAULT_ERROR_DICT


def user_profile_get(nickname):
    with connection.xact():
        user_select = connection.prepare('SELECT * FROM "user" WHERE nickname = $1::CITEXT')
        user = user_select.first(nickname)
    if user:
        resp = flush_dictionary(
            {'nickname': user[1], 'about': user[2], 'email': user[3], 'fullname': user[4]})
        return resp, 200
    else:
        resp = DEFAULT_ERROR_DICT
        return resp, 404


def user_profile_update(nickname, payload):
    about = payload.get('about')
    email = payload.get('email')
    fullname = payload.get('fullname')
    try:
        with connection.xact():
            if payload:
                user_update = connection.prepare('''UPDATE "user" SET about = coalesce($2, about), 
                                                 email = coalesce($3, email),
                                                 fullname = coalesce($4, fullname) 
                                                 WHERE nickname = $1::CITEXT''')
                affected = user_update.first(nickname, about, email, fullname)
                if affected is 0:
                    resp = DEFAULT_ERROR_DICT
                    return resp, 404

            user_select = connection.prepare('SELECT * FROM "user" WHERE nickname = $1::CITEXT')
            user = user_select.first(nickname)
            if user:
                about = user[2]
                email = user[3]
                fullname = user[4]
            else:
                resp = DEFAULT_ERROR_DICT
                return resp, 404
        return {'fullname': fullname, 'email': email, 'nickname': nickname, 'about': about}, 200
    except:
        resp = DEFAULT_ERROR_DICT
        return resp, 409
