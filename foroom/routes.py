from settings import app

base_url = '/api'


def based(url):
    return base_url + url


def response_default(*args):
    return 'Hello. Params: ' + (', '.join(args) or 'sorry, no params passed.')


@app.route('/')
def index():
    return response_default()


@app.route(based('/forum/create'), methods=['POST'])
def forum_create():
    return response_default()


@app.route(based('/forum/<slug>/create'), methods=['POST'])
def forum_thread_create(slug):
    return response_default(slug)


@app.route(based('/forum/<slug>/details'), methods=['GET'])
def forum_details_get(slug):
    return response_default(slug)


@app.route(based('/forum/<slug>/threads'), methods=['GET'])
def forum_threads_get(slug):
    return response_default(slug)


@app.route(based('/post/<id>/details'), methods=['GET'])
def post_details_get(id):
    return response_default(id)


@app.route(based('/post/<id>/details'), methods=['POST'])
def post_details_update(id):
    return response_default(id)


@app.route(based('/service/clear'), methods=['POST'])
def service_clear_database():
    return response_default


@app.route(based('/service/status'), methods=['GET'])
def service_status_get():
    return response_default


@app.route(based('/thread/<slug_or_id>/create'), methods=['POST'])
def thread_post_create(slug_or_id):
    return response_default(slug_or_id)


@app.route(based('/thread/<slug_or_id>/details'), methods=['GET'])
def thread_details_get(slug_or_id):
    return response_default(slug_or_id)


@app.route(based('/thread/<slug_or_id>/details'), methods=['POST'])
def thread_details_update(slug_or_id):
    return response_default(slug_or_id)


@app.route(based('/thread/<slug_or_id>/vote'), methods=['GET'])
def thread_vote(slug_or_id):
    return response_default(slug_or_id)


@app.route(based('/user/<nickname>/create'), methods=['POST'])
def user_create(nickname):
    return response_default(nickname)


@app.route(based('/user/<nickname>/profile'), methods=['GET'])
def user_profile_get(nickname):
    return response_default(nickname)


@app.route(based('/user/<nickname>/profile'), methods=['POST'])
def user_profile_update(nickname):
    return response_default(nickname)
