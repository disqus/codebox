from flask import Flask, session, g
from flaskext.redis import Redis
from flaskext.mail import Mail
from jinja2 import Markup
from urllib import quote

def create_app():
    from codebox.apps.auth.views import auth
    from codebox.apps.auth.models import User
    from codebox.apps.organizations.views import orgs
    from codebox.apps.snippets.views import frontend
    from codebox.utils.syntax import colorize

    app = Flask(__name__)
    app.config.from_object('codebox.conf.Config')

    app.register_module(frontend)
    app.register_module(auth)
    app.register_module(orgs)

    redis = Redis(app)
    redis.init_app(app)
    app.redis = redis
    
    mail = Mail()
    mail.init_app(app)
    app.mail = mail
    
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

