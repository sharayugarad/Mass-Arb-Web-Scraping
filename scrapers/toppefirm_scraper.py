"""
Scraper for toppefirm.com/sitemap.xml
"""
from scrapers.base_scraper import BaseScraper
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ToppeFirmScraper(BaseScraper):
    """Scraper for Toppe Law Firm sitemap."""
    
    def scrape(self) -> dict:
        """
        Scrape URLs from sitemap with date filtering (after Jan 1, 2026).
        
        Returns:
            dict: Scraping results
        """
        try:
            # Get the sitemap
            response = self.get_page(self.source_url)
            
            # Extract URLs and dates from sitemap XML
            url_data = self.extract_urls_from_sitemap(response.text)
            
            logger.info(f"Found {len(url_data)} URLs from sitemap")
            
            # Filter by date (only after Jan 1, 2026)
            # Sitemaps often have lastmod dates, so this works well
            url_data = self.filter_by_date(url_data, require_date=False)
            
            logger.info(f"After date filtering: {len(url_data)} URLs")
            
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