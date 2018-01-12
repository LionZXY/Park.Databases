from settings import connection

from .ext_user_create import user_create
from .ext_user_profile import user_profile_get, user_profile_update
from .ext_forum_create import forum_create
from .ext_forum_details import forum_details_get
from .ext_forum_thread_create import forum_thread_create
from .ext_forum_threads import forum_threads_get
from .ext_thread_post_create import thread_post_create
from .ext_thread_vote import thread_vote
from .ext_thread_details import thread_details_get, thread_details_update
from .ext_thread_posts import thread_posts_get
from .ext_forum_users import forum_users_get
from .ext_post_details import post_details_get, post_details_update
from .ext_service import service_status_get, service_clear

user_select_by_id = connection.prepare('SELECT * FROM "user" WHERE id = $1::BIGINT')
user_select_by_nickname = connection.prepare('SELECT * FROM "user" WHERE nickname = $1::CITEXT')

forum_select_by_id = connection.prepare('SELECT * FROM forum WHERE id = $1::BIGINT')

thread_select_by_id = connection.prepare('SELECT * FROM thread WHERE id = $1::BIGINT')
thread_select_by_slug = connection.prepare('SELECT * FROM thread WHERE slug = $1::CITEXT')
