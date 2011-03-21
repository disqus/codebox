import os
from setuptools import setup, find_packages

setup(name='Code Sharing Thing',
    version='0.1',
    description='',
    user='DISQUS',
    install_requires=[
        # 'python-yammer',
        # https://github.com/sunlightlabs/python-yammer
        'oauth2',
        'Flask-Actions',
        'Flask-Redis',
        'Flask-WTF',
        'dolt',
        'httplib2',
        'simplejson',
        'unittest2',
    ],
    test_suite='unittest2.collector',
    url='http://www.disqus.com',
    packages=find_packages(),
    include_package_data=True,
)
