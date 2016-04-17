#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *  # NOQA

# This file is only used if you use `make publish` or
# explicitly specify it as your config file. You only need to specify values
# that are *different* on the production host.

SITEURL = 'http://www.mamerwiselen.lu'
RELATIVE_URLS = False

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'
FEED_DOMAIN_NAME = SITEURL

DELETE_OUTPUT_DIRECTORY = True
