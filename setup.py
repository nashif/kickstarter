#!/usr/bin/env python

import os, sys
from distutils.core import setup
try:
    import setuptools
    # enable "setup.py develop", optional
except ImportError:
    pass

setup(name='kickstarter',
      version = "0.1",
      description='Kickstarter',
      author='Anas Nashif',
      author_email='anas.nashif@intel.com',
      url='http://meego.com/',
      scripts=['tools/kickstarter'],
      packages=['kickstarter']
     )

