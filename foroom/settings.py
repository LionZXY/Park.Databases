import postgresql
from flask import Flask


app = Flask(__name__)

database_auth_params = {
    'database': 'sample',
    'user': 'sample',
    'host': 'localhost',
    'port': 5432,
    'password': 'sample',
}

connection = postgresql.open(**database_auth_params)
