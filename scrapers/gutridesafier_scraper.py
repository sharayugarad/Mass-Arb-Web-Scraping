"""
Scraper for gutridesafier.com
"""
from scrapers.base_scraper import BaseScraper
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Target pages to scrape
SCRAPE_URLS = [
    'https://www.gutridesafier.com/our-work',
    'https://www.gutridesafier.com/news',
]


class GutrideSafierScraper(BaseScraper):
    """Scraper for Gutride Safier website."""

    DOMAIN = 'gutridesafier.com'

    def scrape(self) -> dict:
        """
        Scrape URLs from all target pages.

        Returns:
            dict: Scraping results
        """
        try:
            combined_url_data = []

            for target_url in SCRAPE_URLS:
                logger.info(f"Scraping target: {target_url}")
                try:
                    response = self.get_page(target_url)

                    url_data = self.extract_urls_from_html_with_dates(
                        response.text,
                        target_url
                    )

                    # Filter to keep only URLs from this domain
                    url_data = [
                        item for item in url_data
                        if self.DOMAIN in item['url']
                    ]

                    logger.info(f"Found {len(url_data)} URLs from {target_url}")
                    combined_url_data.extend(url_data)
                except Exception as e:
                    logger.warning(f"Failed to scrape {target_url}: {e}")

            # Deduplicate across sources
            seen = set()
            unique_url_data = []
            for item in combined_url_data:
                if item['url'] not in seen:
                    seen.add(item['url'])
                    unique_url_data.append(item)
            combined_url_data = unique_url_data

            logger.info(f"Total unique URLs found: {len(combined_url_data)}")

            # Filter by date (only after Jan 1, 2026)
            combined_url_data = self.filter_by_date(combined_url_data, require_date=False)

            logger.info(f"After date filtering: {len(combined_url_data)} URLs")

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise

        new_urls_count, new_urls = self.storage.add_urls_with_dates(
            combined_url_data, self.source_name
        )
        scraped_urls = new_urls

        return {
            'source_name': self.source_name,
            'status': 'success',
            'new_urls': new_urls_count,
            'total_urls': len(self.storage.get_existing_urls()),
            'scraped_urls': scraped_urls,
            'urls_with_dates': sum(1 for item in combined_url_data if item.get('date'))
        }
