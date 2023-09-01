#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple

import goose3
import requests

from . import utils as utl
from .config import TIMEOUT, PROXY, FAKE_USER_AGENT

from goose3 import Goose
from goose3.text import StopWordsChinese

class HttpClient(object):
    """Performs HTTP requests. A `requests` wrapper, essentialy"""

    def __init__(self, timeout=TIMEOUT, proxy=PROXY):
        self.session = requests.session()
        self.session.proxies = self._set_proxy(proxy)
        self.session.headers['User-Agent'] = FAKE_USER_AGENT
        # self.session.headers['Accept-Language'] = 'zh-CN,zh;q=0.8'
        self.goose = Goose({"http_timeout": TIMEOUT, "stopwords_class": StopWordsChinese,"browser_user_agent": FAKE_USER_AGENT})
        self.timeout = timeout
        self.response = namedtuple('response', ['http', 'html'])

    def get(self, page: str):
        """Submits a HTTP GET request."""
        page = self._quote(page)
        try:
            req = self.goose.extract(page)
            self.session.headers["Referer"] = page
        except goose3.network.NetworkError as NetworkError:
            return self.response(http=NetworkError.status_code, html='')
        return self.response(http=200, html=req.raw_html)


    def post(self, page, data):
        """Submits a HTTP POST request."""
        page = self._quote(page)
        try:
            req = self.goose.extract(page)
            self.session.headers["Referer"] = page
        except goose3.network.NetworkError as NetworkError:
            return self.response(http=NetworkError.status_code, html='')
        return self.response(http=200, html=req.raw_html)


    def _quote(self, url):
        """URL-encodes URLs."""
        if utl.decode_bytes(utl.unquote_url(url)) == utl.decode_bytes(url):
            url = utl.quote_url(url)
        print(url)
        return url

    def _set_proxy(self, proxy):
        """Returns HTTP or SOCKS proxies dictionary."""
        if proxy:
            if not utl.is_url(proxy):
                raise ValueError('Invalid proxy format!')
            proxy = {'http': proxy, 'https': proxy}
        return proxy
