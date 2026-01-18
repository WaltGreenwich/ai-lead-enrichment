"""
Web scraping utilities
"""
from bs4 import BeautifulSoup
import httpx
from typing import Optional, Dict
import asyncio


class WebScraper:
    """Simple web scraper for company websites"""

    def __init__(self):
        self.timeout = 10.0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; LeadEnrichmentBot/1.0)'
        }

    async def scrape_website(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape basic info from company website

        Returns:
            Dict with 'title', 'description', 'text_content'
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)

                if response.status_code != 200:
                    return None

                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract title
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ""

                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get(
                    'content', '').strip() if meta_desc else ""

                # Extract visible text (first 2000 chars)
                # Remove scripts and styles
                for script in soup(["script", "style"]):
                    script.decompose()

                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip()
                          for line in lines for phrase in line.split("  "))
                text_content = ' '.join(
                    chunk for chunk in chunks if chunk)[:2000]

                return {
                    'title': title_text,
                    'description': description,
                    'text_content': text_content,
                    'url': str(response.url)
                }

        except Exception as e:
            print(f"Scraping failed for {url}: {str(e)}")
            return None
