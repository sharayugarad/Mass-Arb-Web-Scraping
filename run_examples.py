"""
Example script demonstrating various ways to use the class action scraper.
"""
from main import ScraperOrchestrator
from config.settings import SOURCES
from scrapers import ClassActionLegalHelpScraper, GutrideSafierScraper
from utils.logger import setup_logger

logger = setup_logger(__name__)


def example_1_run_all_scrapers():
    """Example 1: Run all scrapers with email."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Running all scrapers with email")
    print("=" * 80)
    
    orchestrator = ScraperOrchestrator()
    orchestrator.run(send_email=True)


def example_2_run_without_email():
    """Example 2: Run all scrapers without sending email."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Running all scrapers without email")
    print("=" * 80)
    
    orchestrator = ScraperOrchestrator()
    orchestrator.run(send_email=False)


def example_3_run_single_scraper():
    """Example 3: Run a single scraper."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Running a single scraper (Class Action Legal Help)")
    print("=" * 80)
    
    scraper = ClassActionLegalHelpScraper(
        source_url=SOURCES['classactionlegalhelp']['url'],
        source_name=SOURCES['classactionlegalhelp']['name'],
        json_filename=SOURCES['classactionlegalhelp']['json_file']
    )
    
    result = scraper.run()
    
    print("\nResult:")
    print(f"Source: {result['source_name']}")
    print(f"Status: {result['status']}")
    print(f"New URLs: {result['new_urls']}")
    print(f"Total URLs: {result['total_urls']}")


def example_4_run_multiple_specific_scrapers():
    """Example 4: Run only specific scrapers."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Running specific scrapers only")
    print("=" * 80)
    
    # Define which scrapers to run
    scrapers_to_run = [
        ClassActionLegalHelpScraper(
            SOURCES['classactionlegalhelp']['url'],
            SOURCES['classactionlegalhelp']['name'],
            SOURCES['classactionlegalhelp']['json_file']
        ),
        GutrideSafierScraper(
            SOURCES['gutridesafier']['url'],
            SOURCES['gutridesafier']['name'],
            SOURCES['gutridesafier']['json_file']
        )
    ]
    
    results = {}
    for scraper in scrapers_to_run:
        result = scraper.run()
        results[scraper.source_name] = result
    
    # Print summary
    print("\nResults Summary:")
    for source_name, result in results.items():
        print(f"\n{source_name}:")
        print(f"  Status: {result['status']}")
        print(f"  New URLs: {result['new_urls']}")
        print(f"  Total URLs: {result['total_urls']}")


def example_5_custom_workflow():
    """Example 5: Custom workflow with result processing."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Custom workflow with result processing")
    print("=" * 80)
    
    orchestrator = ScraperOrchestrator()
    results = orchestrator.run_all_scrapers()
    
    # Process results
    high_yield_sources = []
    for source_key, result in results.items():
        if result.get('new_urls', 0) > 10:  # Sources with more than 10 new URLs
            high_yield_sources.append({
                'source': result['source_name'],
                'new_urls': result['new_urls']
            })
    
    if high_yield_sources:
        print("\nHigh-yield sources (>10 new URLs):")
        for source in high_yield_sources:
            print(f"  - {source['source']}: {source['new_urls']} new URLs")
    
    # Send email with results
    orchestrator.email_sender.send_email(results)


def main():
    """Main function to demonstrate examples."""
    print("Class Action Scraper - Usage Examples")
    print("=" * 80)
    print("\nAvailable examples:")
    print("1. Run all scrapers with email")
    print("2. Run all scrapers without email")
    print("3. Run a single scraper")
    print("4. Run specific scrapers only")
    print("5. Custom workflow with result processing")
    
    choice = input("\nEnter example number (1-5) or 'q' to quit: ").strip()
    
    examples = {
        '1': example_1_run_all_scrapers,
        '2': example_2_run_without_email,
        '3': example_3_run_single_scraper,
        '4': example_4_run_multiple_specific_scrapers,
        '5': example_5_custom_workflow
    }
    
    if choice in examples:
        examples[choice]()
    elif choice.lower() == 'q':
        print("Exiting...")
    else:
        print("Invalid choice. Please enter a number between 1-5.")


if __name__ == '__main__':
    main()