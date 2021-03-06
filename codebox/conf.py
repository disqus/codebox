"""
codebox.conf
~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import os
import os.path
import sys
import urlparse

class Config(object):
    DEBUG = os.environ.get('DEBUG', False)
    TESTING = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    SECRET_KEY = os.environ.get('SECRET_KEY', '\x89\x1d\xec\x8eJ\xda=C`\xf3<X\x81\xff\x1e\r{+\x1b\xe1\xd1@ku')
    REDIS_DB = 0
    JANRAIN_API_KEY = os.environ.get('JANRAIN_API_KEY')
    DOMAIN_BLACKLIST = ['gmail.com', 'hotmail.com', 'live.com', 'msn.com', 'yahoo.com', 'googlemail.com', 'facebookmail.com']
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 25
    MAIL_USERNAME = os.environ.get('SENDGRID_USERNAME')
    MAIL_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_DOMAIN = os.environ.get('SENDGRID_DOMAIN', 'codebox.cc')
    DEFAULT_MAIL_SENDER = 'verify@email.codebox.cc'

if os.environ.has_key('SENTRY_DSN'):
    try:
        import raven
        raven.load(os.environ['SENTRY_DSN'], Config.__dict__)
    except:
        print "Unexpected error:", sys.exc_info()

if os.environ.has_key('REDISTOGO_URL'):
    # 'redis://username:password@my.host:6789' 
    urlparse.uses_netloc.append('redis')
    url = urlparse.urlparse(os.environ['REDISTOGO_URL'])
    Config.REDIS_PASSWORD = url.password
    Config.REDIS_HOST = url.hostname
    Config.REDIS_PORT = url.port

class TestingConfig(Config):
    REDIS_DB = 9
    TESTING = True
