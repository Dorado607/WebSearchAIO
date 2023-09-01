#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path as os_path, pardir as os_pardir, name as os_name
from sys import version_info

from fake_useragent import UserAgent

## Python version
PYTHON_VERSION = version_info.major

## Maximum number of pages to search
SEARCH_ENGINE_RESULTS_PAGES = 1

## Maximum number of results to return
SEARCH_ENGINE_RESULTS_NUMS = 5

## HTTP request timeout 
TIMEOUT = 10

## Fake User-Agent string - Google desn't like the default user-agent
ua = UserAgent()
FAKE_USER_AGENT = ua.chrome

## request header
HEADERS = {
    "User-Agent": FAKE_USER_AGENT
}

# full headers
# "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
# "Content-Type": "text/html;charset=utf-8",
# "Accept-Encoding": "gzip, deflate, br, zsdch",
# "Accept-Language": "zh,en;q=0.9",
# "User-Agent": FAKE_USER_AGENT

## Proxy server
PROXY = None
# PROXY = 'http://127.0.0.1:7890'

## TOR proxy server 
TOR = 'socks5h://127.0.0.1:9050'

_base_dir = os_path.abspath(os_path.dirname(os_path.abspath(__file__)))

## Path to output files 
OUTPUT_DIR = os_path.join(_base_dir, 'search_results') + os_path.sep
