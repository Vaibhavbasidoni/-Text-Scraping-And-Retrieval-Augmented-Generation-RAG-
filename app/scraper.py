import feedparser
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
import logging
import html
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsArticleScraper:
    def __init__(self):
        # TOI RSS feeds with more diverse categories
        self.rss_feeds = [
            "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
            "https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms",  # World news
            "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms",    # Tech news
            "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",     # Business news
            "https://timesofindia.indiatimes.com/rssfeeds/4719161.cms"      # Sports news
        ]

    def clean_text(self, text: str) -> str:
        """Clean HTML entities and extra whitespace from text"""
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        text = html.unescape(text)
        text = ' '.join(text.split())
        return text

    def scrape_articles(self) -> List[Dict]:
        """
        Fetches news articles from Times of India RSS feeds
        """
        articles = []
        seen_titles = set()  # Track unique titles
        
        try:
            for feed_url in self.rss_feeds:
                logger.info(f"Fetching from RSS feed: {feed_url}")
                
                feed = feedparser.parse(feed_url)
                logger.info(f"Found {len(feed.entries)} entries in feed")
                
                for entry in feed.entries:
                    try:
                        title = self.clean_text(entry.get('title', ''))
                        
                        # Skip if we've seen this title before
                        if title in seen_titles:
                            continue
                            
                        description = self.clean_text(entry.get('description', ''))
                        
                        # Combine title and description for content
                        full_content = f"{title}\n\n{description}"
                            
                        if title and description and len(description) > 50:  # Ensure meaningful content
                            article_data = {
                                'title': title,
                                'content': full_content,
                                'url': entry.get('link', ''),
                                'timestamp': entry.get('published', datetime.now().isoformat())
                            }
                            articles.append(article_data)
                            seen_titles.add(title)
                            logger.info(f"Processed article: {title[:100]}")
                            
                    except Exception as e:
                        logger.error(f"Error processing feed entry: {e}")
                        continue
                        
                time.sleep(1)  # Be polite between feed requests
                
            logger.info(f"Successfully processed {len(articles)} unique articles")
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            
        return articles[:20]  # Limit to 20 most recent unique articles

# Test the scraper
if __name__ == "__main__":
    scraper = NewsArticleScraper()
    articles = scraper.scrape_articles()
    print(f"\nProcessed {len(articles)} articles")
    for article in articles[:2]:
        print(f"\nTitle: {article['title']}")
        print(f"Content preview: {article['content'][:200]}...") 