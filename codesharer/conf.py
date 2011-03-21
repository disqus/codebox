import os, os.path

class Config(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = '\x89\x1d\xec\x8eJ\xda=C`\xf3<X\x81\xff\x1e\r{+\x1b\xe1\xd1@ku'
    REDIS_DB = 0

    PODIO_CLIENT_ID = "dcramer@gmail.com"
    PODIO_KEY = "f7qFIBcPTfTBLOd8ondkO9UGqU6uN1iG"

class TestingConfig(Config):
    REDIS_DB = 9
    TESTING = True
