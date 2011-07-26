"""
codebox.app
~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from flask import Flask, session, g
from flaskext.redis import Redis
from flaskext.mail import Mail
from jinja2 import Markup
from urllib import quote
import logging

def create_app():
    from codebox.apps.auth.views import auth
    from codebox.apps.auth.models import User
    from codebox.apps.organizations.views import orgs
    from codebox.apps.snippets.views import frontend
    from codebox.utils.syntax import colorize

    app = Flask(__name__)
    app.config.from_object('codebox.conf.Config')

    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, app.config['LOG_LEVEL'].upper()))
    app.logger.addHandler(handler)

    app.register_blueprint(auth)
    app.register_blueprint(orgs)
    app.register_blueprint(frontend)

    redis = Redis(app)
    
    app.logger.info("Connected to Redis server at %s:%s" % (app.config['REDIS_HOST'], app.config['REDIS_PORT']))
    
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

