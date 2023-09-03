# !/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from random import uniform as random_uniform
from time import sleep

from bs4 import BeautifulSoup

from . import config as cfg
from . import output as out
from . import utils
from .results import SearchResults
from .persistent_browser import PersistentBrowser


class SearchEngine(object):
    """The base class for all Search Engines."""

    def __init__(self, proxy=cfg.PROXY, timeout=cfg.TIMEOUT):
        """
        :param str proxy: optional, a proxy server
        :param int timeout: optional, the HTTP timeout # not available now
        """
        self._persistent_browser = PersistentBrowser(timeout, proxy)
        self._persistent_browser.start()
        self._delay = (0.01, 1)
        self._query = ''
        self._filters = []

        self.results = SearchResults()
        '''The search results.'''
        self.ignore_duplicate_urls = False
        '''Collects only unique URLs.'''
        self.ignore_duplicate_domains = False
        '''Collects only unique domains.'''
        self.is_banned = False
        '''Indicates if a ban occurred'''

    def _selectors(self, element):
        """Returns the appropriate CSS selector."""
        raise NotImplementedError()

    def _first_page(self):
        """Returns the initial page URL."""
        raise NotImplementedError()

    def _next_page(self, tags):
        """Returns the next page URL and post data."""
        raise NotImplementedError()

    def _get_url(self, tag, item='href'):
        """Returns the URL of search results items."""
        selector = self._selectors('url')
        url = self._get_tag_item(tag.select_one(selector), item)
        return utils.unquote_url(url)

    def _get_title(self, tag, item='text'):
        """Returns the title of search results items."""
        selector = self._selectors('title')
        return self._get_tag_item(tag.select_one(selector), item)

    def _get_text(self, tag, item='text'):
        """Returns the text of search results items."""
        selector = self._selectors('text')
        return self._get_tag_item(tag.select_one(selector), item)

    async def _get_page(self, page: str):
        """Gets pagination links."""
        return await self._persistent_browser.get_raw_html(page)

    def _get_tag_item(self, tag, item):
        """Returns Tag attributes."""
        if not tag:
            return u''
        return tag.text if item == 'text' else tag.get(item, u'')

    def _item(self, link):
        """Returns a dictionary of the link data."""
        return {
            'host': utils.domain(self._get_url(link)),
            'link': self._get_url(link),
            'title': self._get_title(link).strip(),
            'snippet': self._get_text(link).strip()  # from text to snippet to keep up with bing API
        }

    def _query_in(self, item):
        """Checks if query is contained in the item."""
        return self._query.lower() in item.lower()

    def _filter_results(self, soup):
        """Processes and filters the search results."""
        tags = soup.select(self._selectors('links'))
        results = [self._item(l) for l in tags]

        if u'url' in self._filters:
            results = [l for l in results if self._query_in(l['link'])]
        if u'title' in self._filters:
            results = [l for l in results if self._query_in(l['title'])]
        if u'snippet' in self._filters:
            results = [l for l in results if self._query_in(l['snippet'])]
        if u'host' in self._filters:
            results = [l for l in results if self._query_in(utils.domain(l['link']))]

        return results

    def _collect_results(self, items):
        """Collects the search results items."""
        for item in items:
            if not utils.is_url(item['link']):
                continue
            if item in self.results:
                continue
            if self.ignore_duplicate_urls and item['link'] in self.results.links():
                continue
            if self.ignore_duplicate_domains and item['host'] in self.results.hosts():
                continue
            self.results.append(item)

    def _is_ok(self, response):
        """Checks if the HTTP response is 200 OK."""
        self.is_banned = response.http in [403, 429, 503]
        if response.http == 200:
            return True
        msg = ('HTTP ' + str(response.http)) if response.http else response.html
        out.console(msg, level=out.Level.error)
        return False

    def set_search_operator(self, operator):
        """Filters search results based on the operator.
        Supported operators: 'url', 'title', 'text', 'host'

        :param operator: str The search operator(s)
        """
        operators = utils.decode_bytes(operator or u'').lower().split(u',')
        supported_operators = [u'url', u'title', u'text', u'host']

        for operator in operators:
            if operator not in supported_operators:
                msg = u'Ignoring unsupported operator "{}"'.format(operator)
                out.console(msg, level=out.Level.warning)
            else:
                self._filters += [operator]

    async def search(self, query, pages=cfg.SEARCH_ENGINE_RESULTS_PAGES, result_num=cfg.SEARCH_ENGINE_RESULTS_NUMS):
        """Queries the search engine, goes through the pages and collects the results.

        :param query: str The search query
        :param pages: int Optional, the maximum number of results pages to search
        :param result_num: int Optional, the maximum number of results to show

        returns SearchResults object
        """
        out.console('Searching {}'.format(self.__class__.__name__))
        self._query = utils.decode_bytes(query)
        self.results = SearchResults()
        request = self._first_page()

        for page in range(1, pages + 1):
            try:
                response = await self._get_page(request['url'])

                if not self._is_ok(response):
                    break

                tags = BeautifulSoup(response.html, "html.parser")
                items = self._filter_results(tags)
                self._collect_results(items)

                msg = 'page:{:<8} links:{} \n'.format(page, len(self.results))
                out.console(msg, end='')

                if len(self.results) >= result_num:
                    break

                if page < pages:
                    sleep(random_uniform(*self._delay))
                    request = self._next_page(tags)
                    if request['url']:
                        break
                else:
                    break

            except KeyboardInterrupt:
                break

        out.console('', end='')
        output_result = [r for r in self.results]
        return output_result[:result_num] if len(output_result) >= result_num else output_result

    def output(self, output=out.PRINT, path=None):
        """Prints search results and/or creates report files.
        Supported output format: html, csv, json.

        :param output: str Optional, the output format
        :param path: str Optional, the file to save the report
        """
        output = (output or '').lower()
        if not path:
            path = cfg.os_path.join(cfg.OUTPUT_DIR, u'_'.join(self._query.split()))
        out.console('')

        if out.PRINT in output:
            out.print_results([self])
        if out.HTML in output:
            out.write_file(out.create_html_data([self]), path + u'.html')
        if out.CSV in output:
            out.write_file(out.create_csv_data([self]), path + u'.csv')
        if out.JSON in output:
            out.write_file(out.create_json_data([self]), path + u'.json')
