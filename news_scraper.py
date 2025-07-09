import asyncio
from typing import List, Dict
from aiolimiter import AsyncLimiter
from tenacity import retry, stop_after_attempt, wait_exponential

from utils import google_news_url, scrape_google_news, summarize

class NewsScraper:
    _limiter = AsyncLimiter(5, 1)          # 5 req / second

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(min=2, max=10))
    async def scrape_news(self, topics: List[str]) -> Dict[str, str]:
        out = {}
        for t in topics:
            async with self._limiter:
                raw = scrape_google_news(google_news_url(t))
                out[t] = summarize(raw)
                await asyncio.sleep(1)
        return {"news_analysis": out}
