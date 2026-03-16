#!/usr/bin/env python3
"""
Setup script for Class Action Scraper
Helps with initial installation and configuration
"""
import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def check_python_version():
    """Check if Python version is adequate."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Python 3.8 or higher is required!")
        return False
    
    print("✓ Python version is adequate")
    return True


def install_dependencies():
    """Install required packages."""
    print_header("Installing Dependencies")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ ERROR: Failed to install dependencies")
        return False


def create_directories():
    """Create necessary directories."""
    print_header("Creating Directories")
    
    directories = ['data', 'logs']
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True)
            print(f"✓ Created directory: {directory}/")
        else:
            print(f"  Directory already exists: {directory}/")
    
    return True


def setup_env_file():
    """Set up environment file."""
    print_header("Setting Up Environment File")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("  .env file already exists")
        response = input("  Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("  Keeping existing .env file")
            return True
    
    if not env_example.exists():
        print("❌ ERROR: .env.example not found!")
        return False
    
    # Copy example file
    with open(env_example, 'r') as src:
        content = src.read()
    
    with open(env_file, 'w') as dst:
        dst.write(content)
    
    print("✓ Created .env file from .env.example")
    print("\n⚠️  IMPORTANT: You must edit .env file with your email settings!")
    print("   Use a text editor to update:")
    print("   - SENDER_EMAIL")
    print("   - SENDER_PASSWORD")
    print("   - RECIPIENT_EMAIL")
    
    return True


def test_imports():
    """Test if all modules can be imported."""
    print_header("Testing Module Imports")
    
    modules_to_test = [
        'requests',
        'bs4',
        'lxml',
        'dotenv'
    ]
    
    all_ok = True
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"❌ {module} - FAILED")
            all_ok = False
    
    if all_ok:
        print("\n✓ All required modules are available")
    else:
        print("\n❌ Some modules failed to import")
    
    return all_ok


def run_quick_test():
    """Run a quick test of the scraper."""
    print_header("Running Quick Test")
    
    response = input("Do you want to run a quick test scraper? (y/N): ").strip().lower()
    
    if response != 'y':
        print("Skipping test...")
        return True
    
    print("\nRunning test scraper (this may take a few seconds)...")
    
    try:
        from config.settings import SOURCES
        from scrapers import ClassActionLegalHelpScraper
        
        scraper = ClassActionLegalHelpScraper(
            SOURCES['classactionlegalhelp']['url'],
            SOURCES['classactionlegalhelp']['name'],
            SOURCES['classactionlegalhelp']['json_file']
        )
        
        result = scraper.run()
        
        print("\n✓ Test scraper completed successfully!")
        print(f"   Found {result['new_urls']} new URLs")
        print(f"   Total URLs in storage: {result['total_urls']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print_header("Setup Complete!")
    
    print("""
Next Steps:
    
1. Configure Email Settings:
   Edit the .env file with your email credentials:
   
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   RECIPIENT_EMAIL=recipient@example.com
   
   For Gmail: Generate an App Password at
   https://myaccount.google.com/apppasswords

2. Run the Scraper:
   python main.py
   
3. Or try examples:
   python run_examples.py

4. For detailed documentation:
   - README.md (comprehensive guide)
   - QUICKSTART.md (quick reference)

5. Schedule automated runs:
   See README.md for cron (Linux/Mac) or Task Scheduler (Windows) setup

Need help? Check the logs in logs/scraper.log
    """)


def main():
    """Main setup function."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                     Class Action Scraper - Setup Script                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Creating directories", create_directories),
        ("Setting up environment file", setup_env_file),
        ("Testing imports", test_imports),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please fix the errors and run setup again.")
            sys.exit(1)
    
    # Optional test
    run_quick_test()
    
    # Print completion message
    print_next_steps()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)