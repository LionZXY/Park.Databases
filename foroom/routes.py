from flask import request, jsonify
from settings import app
import api


def response_default(json=True, *args):
    response_string = 'Hello. Params: ' + (', '.join(args) or 'sorry, no params passed.')
    if json:
        payload = {
            'message': response_string
        }
        return jsonify(payload)
    return response_string


@app.route('/')
def index_view():
    return response_default()


@app.route(api.get_url('/forum/create'), methods=['POST'])
def forum_create_view():
    payload = request.get_json(silent=True)
    resp, code = api.methods.forum_create(payload)
    return jsonify(resp), code


@app.route(api.get_url('/forum/<slug>/create'), methods=['POST'])
def forum_thread_create_view(slug):
    payload = request.get_json(silent=True)
    resp, code = api.methods.forum_thread_create(slug, payload)
    return jsonify(resp), code


@app.route(api.get_url('/forum/<slug>/details'), methods=['GET'])
def forum_details_get_view(slug):
    resp, code = api.methods.forum_details_get(slug)
    return jsonify(resp), code


@app.route(api.get_url('/forum/<slug>/threads'), methods=['GET'])
def forum_threads_get_view(slug):
    query_args = request.args
    resp, code = api.methods.forum_threads_get(slug, query_args)
    return jsonify(resp), code


@app.route(api.get_url('/forum/<slug>/users'), methods=['GET'])
def forum_users_get(slug):
    query_args = request.args
    resp, code = api.methods.forum_users_get(slug, query_args)
    return jsonify(resp), code
    # return response_default()


@app.route(api.get_url('/post/<post_id>/details'), methods=['GET'])
def post_details_get_view(post_id):
    query_args = request.args
    resp, code = api.methods.post_details_get(post_id, query_args)
    return jsonify(resp), code


@app.route(api.get_url('/post/<post_id>/details'), methods=['POST'])
def post_details_update_view(post_id):
    payload = request.get_json(silent=True)
    resp, code = api.methods.post_details_update(post_id, payload)
    return jsonify(resp), code


@app.route(api.get_url('/service/clear'), methods=['POST'])
def service_clear_database_view():
    resp, code = api.methods.service_clear()
    return jsonify(resp), code
    # return response_default()


@app.route(api.get_url('/service/status'), methods=['GET'])
def service_status_get_view():
    resp, code = api.methods.service_status_get()
    return jsonify(resp), code


@app.route(api.get_url('/thread/<slug_or_id>/create'), methods=['POST'])
def thread_post_create_view(slug_or_id):
    payload = request.get_json(silent=True)
    resp, code = api.methods.thread_post_create(slug_or_id, payload)
    return jsonify(resp), code
    # return response_default(slug_or_id)


@app.route(api.get_url('/thread/<slug_or_id>/details'), methods=['GET'])
def thread_details_get_view(slug_or_id):
    resp, code = api.methods.thread_details_get(slug_or_id)
    return jsonify(resp), code


@app.route(api.get_url('/thread/<slug_or_id>/details'), methods=['POST'])
def thread_details_update_view(slug_or_id):
    payload = request.get_json(silent=True)
    resp, code = api.methods.thread_details_update(slug_or_id, payload)
    return jsonify(resp), code
    # return response_default(slug_or_id)


@app.route(api.get_url('/thread/<slug_or_id>/vote'), methods=['POST'])
def thread_vote_view(slug_or_id):
    payload = request.get_json(silent=True)
    resp, code = api.methods.thread_vote(slug_or_id, payload)
    return jsonify(resp), code


@app.route(api.get_url('/thread/<slug_or_id>/posts'), methods=['GET'])
def thread_posts_get_view(slug_or_id):
    query_args = request.args
    resp, code = api.methods.thread_posts_get(slug_or_id, query_args)
    return jsonify(resp), code


@app.route(api.get_url('/user/<nickname>/create'), methods=['POST'])
def user_create_view(nickname):
    payload = request.get_json(silent=True)
    resp, code = api.methods.user_create(nickname, payload)
    return jsonify(resp), code


@app.route(api.get_url('/user/<nickname>/profile'), methods=['GET'])
def user_profile_get_view(nickname):
    resp, code = api.methods.user_profile_get(nickname)
    return jsonify(resp), code


@app.route(api.get_url('/user/<nickname>/profile'), methods=['POST'])
def user_profile_update_view(nickname):
    payload = request.get_json(silent=True)
    resp, code = api.methods.user_profile_update(nickname, payload)
    return jsonify(resp), code

