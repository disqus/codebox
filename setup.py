from setuptools import setup, find_packages

import os.path

def parse_reqs_file(filepath):
    reqs = []
    with open(filepath, 'r') as fp:
        for line in fp:
            if not line.startswith('-'):
                reqs.append(line)
    return reqs

root = os.path.dirname(__file__)

setup(name='Codebox',
    version='0.1',
    description='',
    author='DISQUS',
    url='http://www.disqus.com',
    install_requires=parse_reqs_file('requirements.txt'),
    test_suite='unittest2.collector',
    packages=find_packages(),
    include_package_data=True,
)
