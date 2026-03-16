"""
Main orchestrator for the class action scraper project.
Coordinates all scrapers and sends email with results.
"""
import sys
from typing import Dict
from config.settings import SOURCES
from utils.logger import setup_logger
from utils.email_sender import EmailSender
from scrapers import (
    ClassActionLegalHelpScraper,
    GutrideSafierScraper,
    FindClassActionScraper,
    ShamisGentileScraper,
    ToppeFirmScraper,
    ConsumersProtectionLawScraper,
    ConsumerLegalActionScraper,
    CrosnerLegalScraper,
    EdelsonScraper,
    StopConsumerHarmScraper,
    EKSMScraper,
    FMFPCScraper,
    LanternLabatonScraper
)

logger = setup_logger(__name__)


class ScraperOrchestrator:
    """Orchestrates the execution of all scrapers and email sending."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.scrapers = self._initialize_scrapers()
        self.email_sender = EmailSender()
        
    def _initialize_scrapers(self) -> dict:
        """
        Initialize all scraper instances.
        
        Returns:
            dict: Dictionary mapping source keys to scraper instances
        """
        scrapers = {
            'classactionlegalhelp': ClassActionLegalHelpScraper(
                SOURCES['classactionlegalhelp']['url'],
                SOURCES['classactionlegalhelp']['name'],
                SOURCES['classactionlegalhelp']['json_file']
            ),
            'gutridesafier': GutrideSafierScraper(
                SOURCES['gutridesafier']['url'],
                SOURCES['gutridesafier']['name'],
                SOURCES['gutridesafier']['json_file']
            ),
            'findclassaction': FindClassActionScraper(
                SOURCES['findclassaction']['url'],
                SOURCES['findclassaction']['name'],
                SOURCES['findclassaction']['json_file']
            ),
            'shamisgentile': ShamisGentileScraper(
                SOURCES['shamisgentile']['url'],
                SOURCES['shamisgentile']['name'],
                SOURCES['shamisgentile']['json_file']
            ),
            'toppefirm': ToppeFirmScraper(
                SOURCES['toppefirm']['url'],
                SOURCES['toppefirm']['name'],
                SOURCES['toppefirm']['json_file']
            ),
            'consumersprotectionlaw': ConsumersProtectionLawScraper(
                SOURCES['consumersprotectionlaw']['url'],
                SOURCES['consumersprotectionlaw']['name'],
                SOURCES['consumersprotectionlaw']['json_file']
            ),
            'consumerlegalaction': ConsumerLegalActionScraper(
                SOURCES['consumerlegalaction']['url'],
                SOURCES['consumerlegalaction']['name'],
                SOURCES['consumerlegalaction']['json_file']
            ),
            'crosnerlegal': CrosnerLegalScraper(
                SOURCES['crosnerlegal']['url'],
                SOURCES['crosnerlegal']['name'],
                SOURCES['crosnerlegal']['json_file']
            ),
            'edelson': EdelsonScraper(
                SOURCES['edelson']['url'],
                SOURCES['edelson']['name'],
                SOURCES['edelson']['json_file']
            ),
            'stopconsumerharm': StopConsumerHarmScraper(
                SOURCES['stopconsumerharm']['url'],
                SOURCES['stopconsumerharm']['name'],
                SOURCES['stopconsumerharm']['json_file']
            ),
            'eksm': EKSMScraper(
                SOURCES['eksm']['url'],
                SOURCES['eksm']['name'],
                SOURCES['eksm']['json_file']
            ),
            'fmfpc': FMFPCScraper(
                SOURCES['fmfpc']['url'],
                SOURCES['fmfpc']['name'],
                SOURCES['fmfpc']['json_file']
            ),
            'lanternlabaton': LanternLabatonScraper(
                SOURCES['lanternlabaton']['url'],
                SOURCES['lanternlabaton']['name'],
                SOURCES['lanternlabaton']['json_file']
            )
        }
        return scrapers
    
    def run_all_scrapers(self) -> Dict[str, Dict]:
        """
        Execute all scrapers.
        
        Returns:
            Dict[str, Dict]: Results from all scrapers
        """
        logger.info("=" * 80)
        logger.info("Starting Class Action Scraper")
        logger.info("=" * 80)
        
        results = {}
        
        for source_key, scraper in self.scrapers.items():
            logger.info(f"\n{'=' * 80}")
            logger.info(f"Processing: {source_key}")
            logger.info(f"{'=' * 80}")
            
            try:
                result = scraper.run()
                results[source_key] = result
                
                # Log summary
                logger.info(f"Completed {source_key}:")
                logger.info(f"  - Status: {result['status']}")
                logger.info(f"  - New URLs: {result['new_urls']}")
                logger.info(f"  - Total URLs: {result['total_urls']}")
                
            except Exception as e:
                logger.error(f"Unexpected error with {source_key}: {e}", exc_info=True)
                results[source_key] = {
                    'source_name': SOURCES[source_key]['name'],
                    'status': 'error',
                    'error': str(e),
                    'new_urls': 0,
                    'total_urls': 0,
                    'scraped_urls': []
                }
        
        return results
    
    def print_summary(self, results: Dict[str, Dict]):
        """
        Print a summary of all scraping results.
        
        Args:
            results: Dictionary containing results from all scrapers
        """
        logger.info("\n" + "=" * 80)
        logger.info("SCRAPING SUMMARY")
        logger.info("=" * 80)
        
        total_new_urls = 0
        total_urls = 0
        successful = 0
        failed = 0
        
        for source_key, result in results.items():
            total_new_urls += result.get('new_urls', 0)
            total_urls += result.get('total_urls', 0)
            
            if result.get('status') == 'success':
                successful += 1
            else:
                failed += 1
        
        logger.info(f"Total Sources: {len(results)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total New URLs: {total_new_urls}")
        logger.info(f"Total URLs in Database: {total_urls}")
        logger.info("=" * 80)
    
    def run(self, send_email: bool = True):
        """
        Execute the complete scraping workflow.
        
        Args:
            send_email: Whether to send email after scraping (default: True)
        """
        try:
            # Run all scrapers
            results = self.run_all_scrapers()
            
            # Print summary
            self.print_summary(results)
            
            # Send email
            if send_email:
                logger.info("\nSending email report...")
                email_sent = self.email_sender.send_email(results)
                
                if email_sent:
                    logger.info("Email sent successfully!")
                else:
                    logger.warning("Failed to send email. Check logs for details.")
            
            logger.info("\n" + "=" * 80)
            logger.info("Scraping completed successfully!")
            logger.info("=" * 80)
            
        except KeyboardInterrupt:
            logger.info("\nScraping interrupted by user.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Fatal error during scraping: {e}", exc_info=True)
            sys.exit(1)


def main():
    """Main entry point for the scraper."""
    orchestrator = ScraperOrchestrator()
    orchestrator.run(send_email=True)


if __name__ == '__main__':
    main()