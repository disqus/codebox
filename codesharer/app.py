from flask import Flask
from flaskext.redis import Redis

def create_app():
    from codesharer.apps.snippets.views import frontend

    app = Flask(__name__)
    app.config.from_object('codesharer.conf.Config')

    app.register_module(frontend)

    db = Redis(app)
    db.init_app(app)
    
    app.db = db

    return app