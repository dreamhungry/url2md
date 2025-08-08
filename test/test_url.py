# coding=utf-8

test_urls = [
    "https://www.datacamp.com/blog/the-top-5-vector-databases",
    "https://www.tigerdata.com/blog/pgvector-vs-qdrant#open-source-vector-database-architecture-comparison",
    "https://python.langchain.com/docs/concepts/architecture/"
]

import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=test_urls[2],
        )
        print(result.markdown)
        with open("test2.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())