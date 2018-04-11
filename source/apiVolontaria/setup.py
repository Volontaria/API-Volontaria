#!/usr/bin/env python
import os
from setuptools import find_packages, setup

install_reqs = list()

try:
    with open('../../requirements.txt') as f:
        install_reqs = f.read().splitlines()
except FileNotFoundError:
    pass

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-api-volontaria',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='API to manage volunteer and order in an organisation.',
    long_description=README,
    url='https://volontaria.github.io/',
    author='Noel Rignon',
    author_email='rignon.noel@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: X.Y',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=install_reqs,
    py_modules=[
        'apiVolontaria',
        'location',
        'order',
        'volunteer',
    ],
)
