from flask import Flask, session, g
from flaskext.redis import Redis
from jinja2 import Markup
from urllib import quote

def create_app():
    from codebox.apps.snippets.views import frontend
    from codebox.apps.auth.views import auth
    from codebox.apps.auth.models import User
    from codebox.utils.syntax import colorize

    app = Flask(__name__)
    app.config.from_object('codebox.conf.Config')

    app.register_module(frontend)
    app.register_module(auth)

    db = Redis(app)
    db.init_app(app)
    
    @app.before_request
    def before_request():
        g.user = None
        
        if 'userid' in session:
            try:
                g.user = User.objects.get(session['userid'])
            except User.DoesNotExist:
                del session['userid']
    
    app.jinja_env.filters['urlencode'] = quote
    def linebreaks(value):
        return Markup(value.replace('\n', '<br/>'))
    
    app.jinja_env.filters['linebreaks'] = linebreaks
    
    app.jinja_env.filters['colorize'] = colorize

    return app

