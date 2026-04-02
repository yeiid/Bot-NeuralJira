import feedparser
import random
from typing import List, Dict

class NewsFetcher:
    """
    Obtiene noticias frescas de diversas fuentes tecnológicas.
    """
    FEEDS = {
        "TechCrunch": "https://techcrunch.com/feed/",
        "Wired": "https://www.wired.com/feed/rss",
        "TheVerge": "https://www.theverge.com/rss/index.xml",
        "Xataka": "https://www.xataka.com/feed/full",  # Español
        "Genbeta": "https://www.genbeta.com/feed/full"  # Español
    }

    def fetch_latest(self, source: str = None) -> List[Dict]:
        """
        Obtiene las últimas noticias. Si no se especifica fuente, elige una al azar.
        """
        if not source:
            source = random.choice(list(self.FEEDS.keys()))
        
        feed_url = self.FEEDS.get(source)
        if not feed_url:
            return []

        feed = feedparser.parse(feed_url)
        entries = []
        
        for entry in feed.entries[:10]: # Tomar las últimas 10
            entries.append({
                "title": entry.title,
                "summary": entry.get("summary", entry.get("description", "")),
                "link": entry.link,
                "source": source,
                "published": entry.get("published", "")
            })
            
        return entries

    def get_random_news_item(self) -> Dict:
        """
        Devuelve una única noticia al azar para ser procesada.
        """
        news = self.fetch_latest()
        if news:
            return random.choice(news)
        return {}

if __name__ == "__main__":
    fetcher = NewsFetcher()
    item = fetcher.get_random_news_item()
    print(f"--- NOTICIA DE HOY ({item.get('source')}) ---")
    print(f"Título: {item.get('title')}")
    print(f"Resumen: {item.get('summary')[:200]}...")
