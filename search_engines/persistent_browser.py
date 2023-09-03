#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import re
import socket
from collections import namedtuple

from fastapi import HTTPException
from playwright.async_api import async_playwright

from search_engines.config import TIMEOUT, PROXY, FAKE_USER_AGENT
from .utils import *


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            return local_ip
    except socket.error as e:
        print(f"Oops! Something went wrong: {e}")
    return None


def is_valid_url(url: str) -> bool:
    pattern = r"^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)$"
    return bool(re.match(pattern, url))


class PersistentBrowser(object):

    def __init__(self, timeout=TIMEOUT, proxy=PROXY):
        self.browser = None
        self.page = None
        self.timeout = timeout
        self.proxy = self._set_proxy(proxy)
        self.user_Agent = FAKE_USER_AGENT
        with open('search_engines/libs/stealth.min.js', 'r') as f:
            self.js = f.read()
        self.response = namedtuple('response', ['http', 'html'])


    async def start(self):
        if self.browser is None:
            playwright = await async_playwright().start()
            chromium = playwright.chromium
            self.browser = await chromium.launch(
                proxy={'server': self.proxy} if self.proxy else None,
                headless=True
            )

    async def stop(self):
        if self.browser is not None:
            await self.browser.close()
            self.browser = None
            self.page = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    @staticmethod
    def _set_proxy(proxy):
        """Returns HTTP or SOCKS proxies dictionary."""
        if proxy is not None:
            if not is_valid_url(proxy):
                raise ValueError('Invalid proxy format!')
            return proxy
        return None

    @staticmethod
    def _quote(url: str):
        """URL-encodes URLs."""
        if decode_bytes(unquote_url(url)) == decode_bytes(url):
            url = quote_url(url)
        print(url)
        return url

    async def get_raw_html(self, request_url: str) -> str:
        context = None
        request_url = self._quote(request_url)
        if is_valid_url(request_url):
            try:
                context = await self.browser.new_context(user_agent=self.user_Agent)
                page = await context.new_page()
                await page.add_init_script(self.js)
                response = await page.goto(request_url)
                raw_html = await page.content()
                await page.screenshot(path="screenshot.png")
                return self.response(http=response.status(), html=raw_html)
            finally:
                if context is not None:  # Check if context is defined and close it
                    await context.close()
        else:
            raise HTTPException(status_code=400, detail="Invalid URL")


if __name__ == "__main__":
    async def get_html(request_url: str):
        async with PersistentBrowser() as pbrowser:
            return await pbrowser.get_raw_html(request_url)


    url = 'https://bot.sannysoft.com/'
    html = asyncio.run(get_html(url))
    print(html)
