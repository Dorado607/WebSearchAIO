#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import socket

from fastapi import FastAPI, HTTPException, Body
from playwright.async_api import async_playwright

app = FastAPI()


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            return local_ip
    except socket.error as e:
        print(f"Oops! Something went wrong: {e}")
    return None


def is_valid_url(url):
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


@app.get("/wsaio/get_title")
async def get_title(request_url: str = Body(..., description="URL")):
    async with PersistentBrowser() as browser:
        if is_valid_url(request_url):
            await browser.page.goto(request_url)
            title = await browser.page.title()
            return {"title": title}
        else:
            raise HTTPException(status_code=400, detail="Invalid URL")


if __name__ == "__main__":
    import uvicorn

    local_ip = get_local_ip()
    uvicorn.run(app, host='localhost', port=1919)
