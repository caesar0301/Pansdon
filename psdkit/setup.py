import os
import sys
from setuptools import setup
from psdkit import __version__

setup(
    name = "psdkit",
    version = __version__,
    url = 'https://github.com/caesar0301/',
    author = 'Xiaming Chen',
    author_email = 'chenxm35@gmail.com',
    description = 'Toolkit for pandidong',
    long_description='''Toolkit for pandidong''',
    license = "Apache License, Version 2.0",
    packages = ['psdkit'],
    keywords = ['tools'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: Freely Distributable',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Topic :: Software Development :: Libraries :: Python Modules',
   ],
)