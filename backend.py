from fastapi import FastAPI, HTTPException, Response
from pathlib import Path
from models import NewsRequest
from reddit_scraper import scrape_reddit_topics
from news_scraper import NewsScraper
from utils import broadcast_script, text_to_mp3
import asyncio

app = FastAPI()

@app.post("/generate-news-audio")
async def generate_news_audio(req: NewsRequest):
    try:
        data = {}
        if req.source_type in {"news", "both"}:
            data["news"] = await NewsScraper().scrape_news(req.topics)
        if req.source_type in {"reddit", "both"}:
            data["reddit"] = await scrape_reddit_topics(req.topics)

        script = broadcast_script(
            data.get("news", {}), data.get("reddit", {}), req.topics
        )
        mp3_path = await asyncio.to_thread(text_to_mp3, script)
        mp3 = Path(mp3_path).read_bytes()
        return Response(
            content=mp3,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=news-summary.mp3"},
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=1234, reload=True)
