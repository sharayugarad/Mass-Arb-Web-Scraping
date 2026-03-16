# """
# Scraper for findclassaction.jotform.com
# """
# from scrapers.base_scraper import BaseScraper
# from utils.logger import setup_logger

# logger = setup_logger(__name__)


# class FindClassActionScraper(BaseScraper):
#     """Scraper for Find Class Action (Jotform) website."""
    
#     def scrape(self) -> dict:
#         """
#         Scrape URLs with date filtering (after Jan 1, 2026).
        
#         Returns:
#             dict: Scraping results
#         """
#         try:
#             # Get the main page
#             response = self.get_page(self.source_url)
            
#             # Extract URLs with dates from HTML
#             url_data = self.extract_urls_from_html_with_dates(
#                 response.text, 
#                 self.source_url
#             )
            
#             # Filter to keep only URLs from jotform.com
#             domain = 'jotform.com'
#             url_data = [item for item in url_data if domain in item['url']]
            
#             logger.info(f"Found {len(url_data)} URLs from {domain}")
            
#             # Filter by date (only after Jan 1, 2026)
#             url_data = self.filter_by_date(url_data, require_date=False)
            
#             logger.info(f"After date filtering: {len(url_data)} URLs")
            
#         except Exception as e:
#             logger.error(f"Error during scraping: {e}")
#             raise
        
#         # # Save to storage with dates
#         # new_urls_count = self.storage.add_urls_with_dates(url_data, self.source_name)
        
#         # # Extract just URLs for the response
#         # scraped_urls = [item['url'] for item in url_data] if new_urls_count > 0 else []

#         new_urls_count, new_urls = self.storage.add_urls_with_dates(url_data, self.source_name)
#         scraped_urls = new_urls

        
#         return {
#             'source_name': self.source_name,
#             'status': 'success',
#             'new_urls': new_urls_count,
#             'total_urls': len(self.storage.get_existing_urls()),
#             'scraped_urls': scraped_urls,
#             'urls_with_dates': sum(1 for item in url_data if item.get('date'))
#         }






"""
Scraper for findclassaction.jotform.com + classaction.org
"""
from scrapers.base_scraper import BaseScraper
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FindClassActionScraper(BaseScraper):
    """Scraper for Find Class Action (Jotform) and ClassAction.org."""

    def scrape(self) -> dict:
        """
        Scrape URLs with date filtering (after Jan 1, 2026) from:
          - https://findclassaction.jotform.com/
          - https://www.classaction.org/

        Returns:
            dict: Scraping results
        """
        try:
            combined_url_data = []

            # ---- 1) Existing Jotform source_url ----
            response = self.get_page(self.source_url)
            jotform_data = self.extract_urls_from_html_with_dates(response.text, self.source_url)

            jotform_domain = "jotform.com"
            jotform_data = [item for item in jotform_data if jotform_domain in item["url"]]

            logger.info(f"Found {len(jotform_data)} URLs from {jotform_domain}")
            combined_url_data.extend(jotform_data)

            # ---- 2) New classaction.org ----
            extra_url = "https://www.classaction.org/"
            response2 = self.get_page(extra_url)
            classaction_data = self.extract_urls_from_html_with_dates(response2.text, extra_url)

            classaction_domain = "classaction.org"
            classaction_data = [item for item in classaction_data if classaction_domain in item["url"]]

            logger.info(f"Found {len(classaction_data)} URLs from {classaction_domain}")
            combined_url_data.extend(classaction_data)

            # ---- Date filter (after Jan 1, 2026) ----
            combined_url_data = self.filter_by_date(combined_url_data, require_date=False)
            logger.info(f"After date filtering (combined): {len(combined_url_data)} URLs")

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise

        # # Save to storage with dates
        # new_urls_count = self.storage.add_urls_with_dates(combined_url_data, self.source_name)

        # # For email output (your current pattern)
        # scraped_urls = [item["url"] for item in combined_url_data] if new_urls_count > 0 else []

        # return {
        #     "source_name": self.source_name,
        #     "status": "success",
        #     "new_urls": new_urls_count,
        #     "total_urls": len(self.storage.get_existing_urls()),
        #     "scraped_urls": scraped_urls,
        #     "urls_with_dates": sum(1 for item in combined_url_data if item.get("date")),
        # }


        # Save to storage with dates (NEW: unpack tuple)
        new_urls_count, new_urls = self.storage.add_urls_with_dates(combined_url_data, self.source_name)

        # For email output: only truly NEW urls (no duplicates)
        scraped_urls = new_urls

        return {
            "source_name": self.source_name,
            "status": "success",
            "new_urls": new_urls_count,
            "total_urls": len(self.storage.get_existing_urls()),
            "scraped_urls": scraped_urls,
            "urls_with_dates": sum(1 for item in combined_url_data if item.get("date")),
}
