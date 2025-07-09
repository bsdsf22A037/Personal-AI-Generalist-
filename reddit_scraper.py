import os
import asyncio
from typing import List, Dict
from datetime import datetime, timedelta

import asyncpraw
from dotenv import load_dotenv

from utils import summarize

load_dotenv()

TWO_WEEKS_AGO = datetime.utcnow() - timedelta(days=14)

async def scrape_reddit_topics(topics: List[str]) -> Dict[str, Dict[str, str]]:
    reddit = asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )

    result = {}

    for topic in topics:
        summaries = []
        try:
            subreddit = await reddit.subreddit("all")
            async for post in subreddit.search(topic, sort="top", time_filter="month", limit=5):
                post_date = datetime.utcfromtimestamp(post.created_utc)
                if post_date < TWO_WEEKS_AGO:
                    continue
                summaries.append(f"{post.title} — {post.selftext[:300]}")

        except Exception as e:
            summaries.append(f"Error fetching Reddit data: {e}")

        full_text = "\n\n".join(summaries) or "No relevant Reddit posts."
        result[topic] = summarize(full_text)
        await asyncio.sleep(1)

    await reddit.close()
    return {"reddit_analysis": result}
