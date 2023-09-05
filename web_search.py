#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from time import sleep

import aiohttp
from fake_useragent import UserAgent
from goose3 import Goose
from goose3.text import StopWordsChinese
from fastapi import FastAPI
from search_engines.engines import *
from search_engines.decorator import atimer

ua = UserAgent()
FAKE_USER_AGENT = ua.chrome


class WSAIO:

    def __init__(self):
        self.loop = None
        self.engine = Bing()
        self.goose = Goose({"stopwords_class": StopWordsChinese, "browser_user_agent": FAKE_USER_AGENT})

    async def process_search_result(self, res, session):
        try:
            extend_snippet = self.goose.extract(url=res["link"])
            if extend_snippet.title:
                res["title"] = extend_snippet.title
            if extend_snippet.cleaned_text:
                abstract = extend_snippet.cleaned_text
                abstract = abstract.replace("\n", "")
                res["snippet"] = abstract
            return res
        except aiohttp.ClientError as connect_error:
            print(connect_error)

    @atimer()
    # 搜索结果增强
    async def search_result_enhancement(self, search_results):
        async with aiohttp.ClientSession() as session:
            tasks = [self.process_search_result(res, session) for res in search_results]
            return await asyncio.gather(*tasks)

    # 异步搜索
    async def asearch(self, query: str, enhance:bool = True):
        search_results = await self.engine.search(query)
        if enhance:
            return await self.search_result_enhancement(search_results)
        return search_results

    def search(self, query: str):
        """
        使用搜索引擎进行搜索，返回搜索结果列表。
        Args: query: 搜索查询字符串。
        Returns: 搜索结果列表，每个结果包含"title"、"link"和"snippet"三个字段。
        """
        if not query:
            return [{
                "snippet": "No input obtained, this may be caused by illegal characters in the question, please try other keywords.",
                "title": "The search engine is experiencing some glitches",
                "link": "https://www.bing.com",
            }]

        self.engine.ignore_duplicate_urls = True  # 避免重复结果
        self.loop = asyncio.get_event_loop()
        search_results = self.loop.run_until_complete(self.asearch(query))

        if not search_results:
            return [{
                "snippet": "No web search results obtained, please try other keywords and wait for a while before trying again",
                "title": "The search engine is experiencing some glitches",
                "link": "https://www.bing.com",
            }]
        else:
            return search_results

wsaio = WSAIO()

@app.get("/search")
def search(query: str): return wsaio.search(query)

if __name__ == "__main__":
    texts = [
        "2杯咖啡",
        "民间借贷利息有什么限制",
        "咖啡，能消炎嗎？",
        "咖啡能消炎吗？黑咖啡有什么功效",
        "房子被洪水淹没，房贷未还完，不知是否继续还贷。",
        "Чи зменшує кава запалення?",
        "コーヒーは炎症を抑えるのか？",
        "Does coffee reduce inflammation?",
    ]

    wsaio = WSAIO()
    for q in texts:
        print(wsaio.search(query=q))
        sleep(4)
