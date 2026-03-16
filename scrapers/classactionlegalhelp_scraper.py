"""
Example scraper for classactionlegalhelp.co with date filtering
"""
from scrapers.base_scraper import BaseScraper
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ClassActionLegalHelpScraper(BaseScraper):
    """Scraper for Class Action Legal Help website with date filtering."""
    
    def scrape(self) -> dict:
        """
        Scrape URLs from classactionlegalhelp.co, filtering for dates after Jan 1, 2026.
        
        Returns:
            dict: Scraping results
        """
        try:
            # Get the main page
            response = self.get_page(self.source_url)
            
            # Extract URLs with dates from HTML
            url_data = self.extract_urls_from_html_with_dates(response.text, self.source_url)
            
            # Filter to keep only URLs from the same domain
            domain = 'classactionlegalhelp.co'
            filtered_by_domain = [item for item in url_data if domain in item['url']]
            
            logger.info(f"Found {len(filtered_by_domain)} URLs from {domain}")
            
            # Filter by date (only after Jan 1, 2026)
            # Set require_date=False to include URLs without dates
            # Set require_date=True to exclude URLs without dates
            filtered_by_date = self.filter_by_date(filtered_by_domain, require_date=False)
            
            logger.info(f"After date filtering: {len(filtered_by_date)} URLs")
            
            # Try to get dates for URLs that don't have them yet
            # by visiting each page (optional, can be slow)
            urls_to_check = [item for item in filtered_by_date if not item.get('date')]
            
            if urls_to_check and len(urls_to_check) <= 10:  # Only check first 10 to save time
                logger.info(f"Checking {len(urls_to_check)} URLs for dates...")
                for item in urls_to_check[:10]:
                    try:
                        page_response = self.get_page(item['url'])
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(page_response.text, 'lxml')
                        date = self.extract_date_from_page(item['url'], soup)
                        if date:
                            item['date'] = date
                    except Exception as e:
                        logger.warning(f"Could not fetch date for {item['url']}: {e}")
                        continue
                
                # Re-filter after getting dates
                filtered_by_date = self.filter_by_date(filtered_by_date, require_date=False)
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise
        
        # Save to storage with dates
        new_urls_count = self.storage.add_urls_with_dates(filtered_by_date, self.source_name)
        
        # Extract just URLs for the response
        scraped_urls = [item['url'] for item in filtered_by_date] if new_urls_count > 0 else []
        
        return {
            'source_name': self.source_name,
            'status': 'success',
            'new_urls': new_urls_count,
            'total_urls': len(self.storage.get_existing_urls()),
            'scraped_urls': scraped_urls,
            'urls_with_dates': sum(1 for item in filtered_by_date if item.get('date'))
        }