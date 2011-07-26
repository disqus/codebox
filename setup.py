from setuptools import setup, find_packages

setup(name='Codebox',
    version='0.1',
    description='',
    user='DISQUS',
    install_requires=[
        'oauth2',
        'dolt',
        'Flask-Actions',
        'Flask-Mail',
        'Flask-Redis',
        'Flask-WTF',
        'httplib2',
        'pygments',
        'simplejson',
        'unittest2',
    ],
    test_suite='unittest2.collector',
    url='http://www.disqus.com',
    packages=find_packages(),
    include_package_data=True,
)
