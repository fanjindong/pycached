import os
import re

from setuptools import setup, find_packages

REQUIRED = []

with open(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'pycached/_version.py')) as fp:
    try:
        version = re.findall(
            r"^__version__ = \"([^']+)\"\r?$", fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

with open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='pycached',
    version=version,
    author='Fan Jindong',
    url='https://github.com/fanjindong/pycached',
    author_email='765912710@qq.com',
    description='multi backend cache',
    long_description=readme,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(),
    install_requires=REQUIRED,
    extras_require={
        'redis"': ['redis>=2.10.6'],
        'msgpack': ['msgpack']
    }
)

# python3.6 setup.py sdist
# twine upload dist/pycached-0.0.4.tar.gz