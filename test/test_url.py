# coding=utf-8
"""
测试下来，绝大部分网站都能把内容很准确的爬下来，效果很好。
TODO:
1. 提出掉多余的部分，一些不属于文章主体的内容也进来了, 解决办法:
    * 手动加规则，把html里面一些不需要的部分剔除
    * 用llm来评判一个部分是不是文章主体
    * 截屏？通过图片就能知道
2. 对于medium这种需要登录才行的网站不行
"""

import datetime

test_urls = [
    "https://www.datacamp.com/blog/the-top-5-vector-databases",
    "https://www.tigerdata.com/blog/pgvector-vs-qdrant#open-source-vector-database-architecture-comparison",
    "https://python.langchain.com/docs/concepts/architecture/",
    "https://www.scrapingbee.com/blog/crawl4ai/"
]

import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=test_urls[0],
        )
        # print(result.markdown)
        print(result.cleaned_html)
        now = datetime.datetime.now()
        format_string = "%Y_%m_%d_%H_%M_%S"
        time_str = now.strftime(format_string)
        # with open(f"../outputs/{time_str}.md", "w", encoding="utf-8") as f:
        #     f.write(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())