#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import re
from time import sleep
from typing import Any, Union

from goose3 import Goose
from goose3.text import StopWordsChinese

from search_engines.config import FAKE_USER_AGENT
from search_engines.engines import Bing

async def web_search(query: str) -> Union[None, list[dict[str, str]], list[dict], Any]:
    """
    使用搜索引擎进行搜索，返回搜索结果列表。

    Args:
        query: 搜索查询字符串。

    Returns:
        搜索结果列表，每个结果包含"title"、"link"和"snippet"三个字段。

    Raises:
        ValueError: 如果搜索引擎API的配置信息未设置，则抛出该异常。
    """

    if not query:
        return [
            {
                "snippet": "No input obtained, this may be caused by illegal characters in the question, please try other keywords.",
                "title": "The search engine is experiencing some glitches",
                "link": "https://www.bing.com",
            }
        ]

    engine = Bing()
    goose = Goose({"stopwords_class": StopWordsChinese,"browser_user_agent": FAKE_USER_AGENT})

    # 设置Bing搜索引擎的参数
    engine.ignore_duplicate_urls = True  # 获取唯一的URL

    # 执行搜索
    search_results = await engine.search(query)

    # 对于每个搜索结果，提取标题和概要内容
    for res in search_results:
        try:
            extend_snippet = goose.extract(url=res["link"])
            if extend_snippet.title:
                res["title"] = extend_snippet.title
            if extend_snippet.cleaned_text:
                abstract = extend_snippet.cleaned_text
                abstract = re.sub("\n", "", abstract)
                res["snippet"] = abstract
        except Exception as connect_error:
            print(connect_error)
            break

    if not search_results:
        return [
            {
                "snippet": "No web search results obtained, please try other keywords and wait for a while before trying again",
                "title": "The search engine is experiencing some glitches",
                "link": "https://www.bing.com",
            }
        ]
    else:
        return search_results


if __name__ == "__main__":
    texts = [
        "民间借贷利息有什么限制",
        "咖啡，能消炎嗎？",
        "咖啡能消炎吗？黑咖啡有什么功效",
        "房子被洪水淹没，房贷未还完，不知是否继续还贷。",
        "Чи зменшує кава запалення?",
        "コーヒーは炎症を抑えるのか？",
        "Does coffee reduce inflammation?",
        "2杯咖啡",
    ]

    for q in texts:
        print(asyncio.run(web_search(query=q)))
        sleep(3)
