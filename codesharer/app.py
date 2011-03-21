from flask import Flask
from flaskext.redis import Redis


def create_app():
    from codesharer.apps.snippets.views import frontend
    from codesharer.apps.auth.views import auth

    app = Flask(__name__)
    app.config.from_object('codesharer.conf.Config')

    app.register_module(frontend)
    app.register_module(auth)
    #app.register_module(yammer)

    db = Redis(app)
    db.init_app(app)

    app.db = db

    from codesharer.utils.syntax import colorize
    app.jinja_env.filters['colorize'] = colorize

    return app
