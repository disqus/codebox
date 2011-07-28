"""
codebox
~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from flask import Flask, session, g, request, abort
from flaskext.redis import Redis
from flaskext.mail import Mail
from jinja2 import Markup
from urllib import quote
from werkzeug.routing import BaseConverter
import logging

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('codebox').version
except Exception, e:
    VERSION = 'unknown'

class UUIDConverter(BaseConverter):
    regex = '[a-zA-Z0-9]{32}'

app = Flask(__name__)
app.config.from_object('codebox.conf.Config')

def configure_logging(app):
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, app.config['LOG_LEVEL'].upper()))

    root = logging.getLogger()
    root.setLevel(logging.WARNING)
    root.addHandler(handler)

    app.logger.addHandler(handler)

configure_logging(app)

app.url_map.converters['uuid'] = UUIDConverter

redis = Redis(app)

app.logger.info("Connected to Redis server at %s:%s" % (app.config['REDIS_HOST'], app.config['REDIS_PORT']))

mail = Mail()
mail.init_app(app)

@app.before_request
def before_request():
    from codebox.apps.auth.models import User

    g.user = None
    g.is_api = False
    
    if 'userid' in session:
        try:
            g.user = User.objects.get(session['userid'])
        except User.DoesNotExist:
            del session['userid']
    
    api_token = request.form.get('api_token', request.args.get('api_token', '')).strip()
    if api_token:
        try:
            g.user = User.objects.filter(api_token=api_token)[0]
            g.is_api = True
        except IndexError:
            return abort(403)

app.jinja_env.filters['urlencode'] = quote
def linebreaks(value):
    return Markup(value.replace('\n', '<br/>'))

app.jinja_env.filters['linebreaks'] = linebreaks

from codebox.utils.syntax import colorize
app.jinja_env.filters['colorize'] = colorize

import codebox.apps.auth.views
import codebox.apps.organizations.views
import codebox.apps.snippets.views