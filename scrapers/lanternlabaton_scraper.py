"""
Scraper for lantern.labaton.com
"""
from scrapers.base_scraper import BaseScraper
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Target pages to scrape (paginated HTML sources)
SCRAPE_URLS = [
    'https://lantern.labaton.com/news-and-insights',
    'https://lantern.labaton.com/explore-cases',
]


class LanternLabatonScraper(BaseScraper):
    """Scraper for Lantern by Labaton website (HTML-based, multi-page)."""

    # Domain used to filter extracted links to this site only
    DOMAIN = 'lantern.labaton.com'

    # Relevant path prefixes to keep (case pages and news articles)
    RELEVANT_PATHS = ('/case/', '/news/')

    # Maximum number of pagination pages to follow per source URL
    MAX_PAGES = 50

    def _scrape_paginated_url(self, base_url: str) -> list:
        """
        Scrape all pagination pages for a given base URL.

        Iterates through ?page=1, ?page=2, ... until no new relevant
        URLs are found or MAX_PAGES is reached.

        Args:
            base_url: The starting URL (e.g. https://lantern.labaton.com/explore-cases)

        Returns:
            list: Combined url_data dicts from all pages
        """
        all_url_data = []
        seen_urls = set()

        for page_num in range(1, self.MAX_PAGES + 1):
            page_url = f"{base_url}?page={page_num}"
            logger.info(f"Fetching page {page_num}: {page_url}")

            try:
                response = self.get_page(page_url)
            except Exception as e:
                logger.warning(f"Failed to fetch {page_url}: {e}")
                break

            # Extract URLs with dates from the HTML page
            page_data = self.extract_urls_from_html_with_dates(
                response.text,
                page_url
            )

            # Filter to keep only links on this domain
            page_data = [
                item for item in page_data
                if self.DOMAIN in item['url']
            ]

            # Filter to keep only relevant paths (/case/ and /news/)
            page_data = [
                item for item in page_data
                if any(path in item['url'] for path in self.RELEVANT_PATHS)
            ]

            # Check for new URLs on this page (stop if none found)
            new_on_page = [
                item for item in page_data
                if item['url'] not in seen_urls
            ]

            if not new_on_page:
                logger.info(f"No new URLs found on page {page_num}, stopping pagination")
                break

            for item in new_on_page:
                seen_urls.add(item['url'])

            all_url_data.extend(new_on_page)
            logger.info(f"Page {page_num}: found {len(new_on_page)} new URLs")

        return all_url_data

    def scrape(self) -> dict:
        """
        Scrape case and news URLs from all target pages.

        Iterates through SCRAPE_URLS, paginates each one, extracts
        relevant links, filters by date, and stores new URLs.

        Returns:
            dict: Scraping results
        """
        try:
            combined_url_data = []

            for target_url in SCRAPE_URLS:
                logger.info(f"Scraping target: {target_url}")
                url_data = self._scrape_paginated_url(target_url)
                logger.info(f"Found {len(url_data)} URLs from {target_url}")
                combined_url_data.extend(url_data)

            # Deduplicate across sources (a URL may appear on both pages)
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
