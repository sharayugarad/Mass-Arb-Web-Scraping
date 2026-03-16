"""
Scraper for fmfpc.com
"""
from scrapers.base_scraper import BaseScraper
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Target pages to scrape (sitemaps and HTML sources)
SCRAPE_URLS = [
    'https://www.fmfpc.com/pages-sitemap.xml',
    'https://www.fmfpc.com/store-products-sitemap.xml',
    'https://www.fmfpc.com/store-categories-sitemap.xml',
    'https://www.fmfpc.com/results',
]


class FMFPCScraper(BaseScraper):
    """Scraper for FMFPC website."""

    DOMAIN = 'fmfpc.com'

    def _is_sitemap_url(self, url: str) -> bool:
        """Check if a URL points to a sitemap XML file."""
        return url.endswith('.xml')

    def _scrape_single_url(self, target_url: str) -> list:
        """
        Scrape a single target URL (sitemap or HTML page).

        Args:
            target_url: The URL to scrape

        Returns:
            list: url_data dicts extracted from this source
        """
        response = self.get_page(target_url)

        if self._is_sitemap_url(target_url):
            url_data = self.extract_urls_from_sitemap(response.text)
        else:
            url_data = self.extract_urls_from_html_with_dates(
                response.text,
                target_url
            )

        # Filter to keep only URLs from this domain
        url_data = [
            item for item in url_data
            if self.DOMAIN in item['url']
        ]

        return url_data

    def scrape(self) -> dict:
        """
        Scrape URLs from all target pages (sitemaps and HTML).

        Returns:
            dict: Scraping results
        """
        try:
            combined_url_data = []

            for target_url in SCRAPE_URLS:
                logger.info(f"Scraping target: {target_url}")
                try:
                    url_data = self._scrape_single_url(target_url)
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
