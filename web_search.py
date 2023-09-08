#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import asyncio
import logging
import socket
from typing import Any

import aiohttp
import pydantic
import uvicorn
from fake_useragent import UserAgent
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from goose3 import Goose
from goose3.text import StopWordsChinese
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from search_engines.config import OPEN_CROSS_DOMAIN, WEB_SEARCH_ENGINE
from search_engines.decorator import atimer
from search_engines.engines import *

ua = UserAgent()
FAKE_USER_AGENT = ua.edge


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            return local_ip
    except socket.error as e:
        print("Error occurred when getting ip", e)
        return None


class WSAIO:

    def __init__(self):
        self.engine = None
        self.loop = None
        self.select_search_engine()
        self.goose = Goose({"stopwords_class": StopWordsChinese, "browser_user_agent": FAKE_USER_AGENT})

    def select_search_engine(self):
        match WEB_SEARCH_ENGINE:
            case 'bing':
                self.engine = Bing()
            case 'google':
                self.engine = Google()
            case 'duckduckgo':
                self.engine = Duckduckgo()
            # add your case here

    async def process_search_result(self, res, session):
        try:
            async with session.get(url=res["link"]) as response:
                raw_html = await response.text()
                extend_snippet = self.goose.extract(raw_html=raw_html)
                if extend_snippet.title:
                    res["title"] = extend_snippet.title
                if extend_snippet.cleaned_text:
                    abstract = extend_snippet.cleaned_text
                    abstract = abstract.replace("\n", "")
                    res["snippet"] = abstract
                return res
        except aiohttp.ClientError as connect_error:
            logging.error(connect_error)

    @atimer()
    # search results enhancement
    async def search_result_enhancement(self, search_results):
        async with aiohttp.ClientSession() as session:
            coroutines = [self.process_search_result(res, session) for res in search_results]
            enhanced_results = await asyncio.gather(*coroutines)
            return enhanced_results

    # async search
    async def asearch(self, query: str, enhance: bool = True):
        search_results = await self.engine.search(query)
        if enhance:
            return await self.search_result_enhancement(search_results)
        return search_results

    async def search(self, query: str = Query(..., description="Query", examples=["string"])):
        """
        Use a search engine to perform a search and return a list of search results.
        Args: query: The search query string.
        Returns: A list of search results, each containing “title”, “link”, and “snippet” fields.
        """
        if not query:
            return ListResultResponse(
                data=[{
                    "snippet": "No input obtained, this may be caused by illegal characters in the question, please try other keywords.",
                    "title": "The search engine is experiencing some glitches",
                    "link": "https://www.bing.com",
                }]
            )

        self.engine.ignore_duplicate_urls = True  # avoid duplicate url results
        # self.loop = asyncio.get_event_loop()
        # search_results = self.loop.run_until_complete(self.asearch(query))
        search_results = await self.asearch(query)


        if not search_results:
            return ListResultResponse(
                data=[{
                    "snippet": "No web search results obtained, please try other keywords and wait for a while before trying again",
                    "title": "The search engine is experiencing some glitches",
                    "link": "https://www.bing.com",
                }]
            )
        else:
            return ListResultResponse(
                data=search_results
            )


class BaseResponse(BaseModel):
    code: int = pydantic.Field(200, description="HTTP status code")
    msg: str = pydantic.Field("success", description="HTTP status message")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
            }
        }


class ListResultResponse(BaseResponse):
    data: list[dict[str, Any]] = pydantic.Field(..., description="List of search results")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": [{'host': 'host', 'link': 'url', 'title': 'string', 'snippet': 'string'}],
            }
        }


async def document():
    return RedirectResponse(url="/docs")


# init fastapi
app = FastAPI()
if OPEN_CROSS_DOMAIN:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# init engine
wsaio = WSAIO()

# add route
app.post('/search', response_model=ListResultResponse, summary='get search results')(wsaio.search)
app.get("/", response_model=BaseResponse, summary="swagger Document")(document)


# launch api
def api_start(host, port, **kwargs):
    if kwargs.get("ssl_keyfile") and kwargs.get("ssl_certfile"):
        uvicorn.run(app, host=host, port=port, ssl_keyfile=kwargs.get("ssl_keyfile"),
                    ssl_certfile=kwargs.get("ssl_certfile"))
    else:
        uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web Search Engine All in One')
    # parser.add_argument("--host", type=str, default=get_local_ip())
    parser.add_argument("--host", type=str, default='127.0.0.1')
    parser.add_argument("--port", type=int, default=1919)
    parser.add_argument("--ssl_keyfile", type=str)
    parser.add_argument("--ssl_certfile", type=str)

    # 初始化消息
    args = parser.parse_args()
    args_dict = vars(args)
    api_start(args.host, args.port, ssl_keyfile=args.ssl_keyfile, ssl_certfile=args.ssl_certfile)
