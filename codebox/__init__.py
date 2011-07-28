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

handler = logging.StreamHandler()
handler.setLevel(getattr(logging, app.config['LOG_LEVEL'].upper()))
app.logger.addHandler(handler)

app.url_map.converters['uuid'] = UUIDConverter

redis = Redis(app)

app.logger.info("Connected to Redis server at %s:%s" % (app.config['REDIS_HOST'], app.config['REDIS_PORT']))

mail = Mail()
mail.init_app(app)

@app.before_request
def before_request():
    from codebox.apps.auth.models import User

    g.user = None
    
    if 'userid' in session:
        try:
            g.user = User.objects.get(session['userid'])
        except User.DoesNotExist:
            del session['userid']
    elif 'api_token' in request.form:
        try:
            g.user = User.objects.filter(api_token=request.form['api_token'])
        except User.DoesNotExist:
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