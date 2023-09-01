#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT
from ..engine import SearchEngine


class Sougou(SearchEngine):
    """Searches sougou.com"""

    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Sougou, self).__init__(proxy, timeout)
        self._base_url = u'https://www.sogou.com/'
        self.set_headers({'User-Agent': FAKE_USER_AGENT})

    def _selectors(self, element):
        """Returns the appropriate CSS selector."""
        selectors = {
            'url': 'a[href]',
            'title': 'h3',
            'text': 'p',
            'links': 'div.vrwrap',
            'next': '#sogou_next'
        }
        return selectors[element]

    def _first_page(self):
        """Returns the initial page and query."""
        self._get_page(self._base_url)
        url = u'{}web?query={}&page=1&ie=utf8'.format(self._base_url, self._query)
        return {'url': url, 'data': None}

    def _next_page(self, tags):
        """Returns the next page URL and post data (if any)"""
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = None
        if next_page:
            url = (self._base_url + next_page)
        return {'url': url, 'data': None}
