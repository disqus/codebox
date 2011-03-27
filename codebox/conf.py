import os, os.path

class Config(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = '\x89\x1d\xec\x8eJ\xda=C`\xf3<X\x81\xff\x1e\r{+\x1b\xe1\xd1@ku'
    REDIS_DB = 0
    JANRAIN_API_KEY = '288a1ca2fedb4e1d1780c320fa4082ae69640a52'
    PODIO_CLIENT_ID = "dcramer@gmail.com"
    PODIO_KEY = "f7qFIBcPTfTBLOd8ondkO9UGqU6uN1iG"
    DOMAIN_BLACKLIST = ['gmail.com', 'hotmail.com', 'live.com', 'msn.com', 'yahoo.com', 'googlemail.com', 'facebookmail.com']

class TestingConfig(Config):
    REDIS_DB = 9
    TESTING = True
