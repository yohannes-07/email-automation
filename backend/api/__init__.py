import os, json

from flask import Flask
from flask_cors import CORS

from .models import db, seed_admin
from .routes import rest_api

app = Flask(__name__)

app.config.from_object('api.config.BaseConfig')
CORS(app, origins='http://frontend:3000', supports_credentials=True)

db.init_app(app)
rest_api.init_app(app)


@app.before_request
def initialize_database():
    try:
        
        db.create_all()
    except Exception as e:

        print('> Error: DBMS Exception: ' + str(e) )

        # fallback to SQLite
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')

        print('> Fallback to SQLite ')
        db.create_all()

    seed_admin()

@app.after_request
def after_request(response):

    if int(response.status_code) >= 400:
        response_data = json.loads(response.get_data())
        if "errors" in response_data:
            response_data = {"success": False,
                             "msg": list(response_data["errors"].items())[0][1]}
            response.set_data(json.dumps(response_data))
        response.headers.add('Content-Type', 'application/json')
    return response