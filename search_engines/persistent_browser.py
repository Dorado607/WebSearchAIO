#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import re
import socket

from fastapi import HTTPException
from playwright.async_api import async_playwright


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


class PersistentBrowser:

    def __init__(self):
        self.browser = None
        self.page = None

    async def start(self):
        if self.browser is None:
            playwright = await async_playwright().start()
            chromium = playwright.chromium
            self.browser = await chromium.launch()
            self.page = await self.browser.new_page()

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

    async def get_raw_html(self, request_url: str) -> str:
        if is_valid_url(request_url):
            await self.page.goto(request_url)
            return await self.page.content()
        else:
            raise HTTPException(status_code=400, detail="Invalid URL")


if __name__ == "__main__":
    async def get_html(request_url: str):
        async with PersistentBrowser() as pbrowser:
            return await pbrowser.get_raw_html(request_url)


    url = 'https://www.bing.com/search?&q=%D0%A7%D0%B8+%D0%B7%D0%BC%D0%B5%D0%BD%D1%88%D1%83%D1%94+%D0%BA%D0%B0%D0%B2%D0%B0+%D0%B7%D0%B0%D0%BF%D0%B0%D0%BB%D0%B5%D0%BD%D0%BD%D1%8F'
    html = asyncio.run(get_html(url))
    print(html)
