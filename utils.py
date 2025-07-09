import os, datetime as dt, requests
from urllib.parse import quote_plus
from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup
from newspaper import Article
from gtts import gTTS
from transformers import pipeline
import feedparser
from urllib.parse import quote_plus

_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize(text: str, max_len: int = 140, min_len: int = 30) -> str:
    if not text.strip(): return ""
    input_words = len(text.split())
    if input_words < min_len:
        return text.strip()
    adjusted_max_len = min(max_len, int(input_words * 0.6) + min_len)
    out = _summarizer(text, max_length=adjusted_max_len, min_length=min_len, do_sample=False)
    return out[0]["summary_text"]

def google_news_url(keyword: str,
                    lang: str = "en",
                    country: str = "PK") -> str:
    # Google News uses  q=, not the obsolete for=
    # RSS feed is reliable and far easier to parse  :contentReference[oaicite:0]{index=0}
    return (f"https://news.google.com/rss/search?"
            f"q={quote_plus(keyword)}&hl={lang}-{country}"
            f"&gl={country}&ceid={country}:{lang}")

def scrape_google_news(url: str, max_items: int = 5) -> str:
    feed = feedparser.parse(url)
    items = feed.entries[:max_items]
    if not items:
        return "No articles found."
    snippets = [f"{e.title}: {e.summary[:200]}…" for e in items]
    return "\n".join(snippets)

    for a in soup.find_all("a", class_="DY5T1d")[:3]:
        link = "https://news.google.com" + a["href"][1:]
        try:
            art = Article(link)
            art.download(); art.parse()
            results.append(f"{art.title}: {art.text[:300]}…")
        except:
            continue

    return "\n".join(results) if results else "No articles found."

def broadcast_script(news: Dict, reddit: Dict, topics: List[str]) -> str:
    out: List[str] = []
    for t in topics:
        n = news.get("news_analysis", {}).get(t, "")
        r = reddit.get("reddit_analysis", {}).get(t, "")
        if not (n or r): continue
        out.append(f"Topic: {t}.")
        if n: out.append(f"According to news sources: {n}")
        if r: out.append(f"On Reddit, users shared: {r}")
        out.append("To wrap up this segment.\n")
    return "\n".join(out)

def text_to_mp3(text: str, dir_: str = "audio") -> str:
    Path(dir_).mkdir(exist_ok=True)
    fname = Path(dir_) / f"tts_{dt.datetime.now():%Y%m%d_%H%M%S}.mp3"
    gTTS(text).save(fname)
    return str(fname)
