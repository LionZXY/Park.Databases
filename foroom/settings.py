import postgresql
from flask import Flask


app = Flask(__name__)

database_auth_params = {
    'database': 'docker',
    'user': 'docker',
    'host': 'localhost',
    'port': 5432,
    'password': 'docker',
}

connection = postgresql.open(**database_auth_params)
