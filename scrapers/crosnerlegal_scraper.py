"""
Scraper for crosnerlegal.com/sitemap_index.xml
"""
from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from utils.logger import setup_logger

logger = setup_logger(__name__)


class CrosnerLegalScraper(BaseScraper):
    """Scraper for Crosner Legal sitemap index."""
    
    def scrape(self) -> dict:
        """
        Scrape URLs from sitemap index with date filtering (after Jan 1, 2026).
        
        Returns:
            dict: Scraping results
        """
        url_data = []
        
        try:
            # Get the sitemap index
            response = self.get_page(self.source_url)
            
            # Parse sitemap index to find individual sitemaps
            soup = BeautifulSoup(response.text, 'lxml-xml')
            sitemap_urls = [loc.text.strip() for loc in soup.find_all('loc')]
            
            logger.info(f"Found {len(sitemap_urls)} sitemaps in the index")
            
            # Fetch each sitemap and extract URLs
            for sitemap_url in sitemap_urls:
                try:
                    sitemap_response = self.get_page(sitemap_url)
                    sitemap_urls_data = self.extract_urls_from_sitemap(sitemap_response.text)
                    url_data.extend(sitemap_urls_data)
                    logger.info(f"Extracted {len(sitemap_urls_data)} URLs from {sitemap_url}")
                except Exception as e:
                    logger.warning(f"Error fetching sitemap {sitemap_url}: {e}")
                    continue
            
            logger.info(f"Found {len(url_data)} total URLs from all sitemaps")

            # Case URLs are included regardless of lastmod date (many have old dates but are still valid)
            # Non-case URLs are filtered to only include those after Jan 1, 2026
            case_url_data = [item for item in url_data if '/case/' in item.get('url', '')]
            other_url_data = [item for item in url_data if '/case/' not in item.get('url', '')]

            filtered_other = self.filter_by_date(other_url_data, require_date=False)
            url_data = case_url_data + filtered_other

            logger.info(f"After date filtering: {len(url_data)} URLs ({len(case_url_data)} case URLs + {len(filtered_other)} other URLs)")
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise
        
        # # Save to storage with dates
        # new_urls_count = self.storage.add_urls_with_dates(url_data, self.source_name)
        
        # # Extract just URLs for the response
        # scraped_urls = [item['url'] for item in url_data] if new_urls_count > 0 else []

        new_urls_count, new_urls = self.storage.add_urls_with_dates(url_data, self.source_name)
        scraped_urls = new_urls

        
        return {
            'source_name': self.source_name,
            'status': 'success',
            'new_urls': new_urls_count,
            'total_urls': len(self.storage.get_existing_urls()),
            'scraped_urls': scraped_urls,
            'urls_with_dates': sum(1 for item in url_data if item.get('date'))
        }