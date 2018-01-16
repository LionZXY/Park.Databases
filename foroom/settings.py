import postgresql
from flask import Flask


app = Flask(__name__)

database_auth_params = {
    'database': 'technopark',
    'user': 'lionzxy',
    'host': 'localhost',
    'port': 5432,
    'password': '123456789',
}

connection = postgresql.open(**database_auth_params)
