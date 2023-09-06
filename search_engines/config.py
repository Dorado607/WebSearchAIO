#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path as os_path
from sys import version_info

from fake_useragent import UserAgent

# Python version
PYTHON_VERSION = version_info.major

# Maximum number of pages to search
SEARCH_ENGINE_RESULTS_PAGES = 1

# Maximum number of results to return
SEARCH_ENGINE_RESULTS_NUMS = 4

# browser waiting timeout
TIMEOUT = 30000

# Proxy server
PROXY = None
# PROXY = 'http://127.0.0.1:7890'

# TOR proxy server
TOR = 'socks5h://127.0.0.1:9050'

_base_dir = os_path.abspath(os_path.dirname(os_path.abspath(__file__)))

# Path to output files
OUTPUT_DIR = os_path.join(_base_dir, 'search_results') + os_path.sep

# set OPEN_CROSS_DOMAIN = True to allow cross-domain
OPEN_CROSS_DOMAIN = False
