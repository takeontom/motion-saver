#!/usr/bin/env python
from os import path

from setuptools import setup

readme = path.join(path.abspath(path.dirname(__file__)), 'README.rst')
with open(readme, encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='motion-saver',
    version='0.1.0',
    description='Library to pick out motion from a stream of images.',
    long_description=long_description,
    author='Tom Smith',
    author_email='tom@takeontom.com',
    url='https://github.com/takeontom/motion-saver',
    packages=['motionsaver'],
    install_requires=('pillow>=4', ),
    license='MIT license',
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ),
)
