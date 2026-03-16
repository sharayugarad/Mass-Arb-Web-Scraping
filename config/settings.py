"""
Configuration module for the class action scraper project.
"""
import os
from pathlib import Path

# Path to the secrets env file (update this to the actual location)
from dotenv import load_dotenv
SECRETS_ENV_PATH = Path('/Users/sharayu/CodeLab/Local Secrets/secrets.local.env')

if SECRETS_ENV_PATH.exists():
    load_dotenv(dotenv_path=SECRETS_ENV_PATH)
else:
    print(
        f"WARNING: Secrets file not found at {SECRETS_ENV_PATH}. "
        f"Update SECRETS_ENV_PATH in config/settings.py to the correct location."
    )

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'
CONFIG_DIR = BASE_DIR / 'config'

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Load Email Configuration from environment variables (.env file)
def load_email_config():
    """Load email configuration from environment variables."""
    receiver_emails_raw = os.getenv('RECEIVER_EMAILS', '')
    receiver_emails = [
        email.strip() for email in receiver_emails_raw.split(',') if email.strip()
    ]

    config = {
        'smtp_server': os.getenv('SMTP_SERVER', ''),
        'smtp_port': int(os.getenv('SMTP_PORT', 0)),
        'use_ssl': os.getenv('USE_SSL', 'false').lower() == 'true',
        'sender_email': os.getenv('SENDER_EMAIL', ''),
        'sender_password': os.getenv('SENDER_PASSWORD', ''),
        'receiver_emails': receiver_emails,
    }

    # Validate required fields — no fallback, warn clearly
    missing = []
    if not config['smtp_server']:
        missing.append('SMTP_SERVER')
    if not config['smtp_port']:
        missing.append('SMTP_PORT')
    if not config['sender_email']:
        missing.append('SENDER_EMAIL')
    if not config['sender_password']:
        missing.append('SENDER_PASSWORD')
    if not config['receiver_emails']:
        missing.append('RECEIVER_EMAILS')

    if missing:
        print(
            f"WARNING: Missing email environment variables: {', '.join(missing)}. "
            f"Email functionality will not work. "
            f"Set these variables in your .env file."
        )

    return config

EMAIL_CONFIG = load_email_config()

# Scraping Configuration (use environment variables or defaults)
SCRAPING_CONFIG = {
    'request_timeout': int(os.getenv('REQUEST_TIMEOUT', 30)),
    'max_retries': int(os.getenv('MAX_RETRIES', 3)),
    'delay_between_requests': float(os.getenv('DELAY_BETWEEN_REQUESTS', 1)),
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Source URLs Configuration
SOURCES = {
    'classactionlegalhelp': {
        'url': 'https://www.classactionlegalhelp.co/',
        'name': 'Class Action Legal Help',
        'json_file': 'classactionlegalhelp_urls.json'
    },
    'gutridesafier': {
        'url': 'https://www.gutridesafier.com/',
        'name': 'Gutride Safier Investigations',
        'json_file': 'gutridesafier_urls.json'
    },
    'findclassaction': {
        'url': 'https://findclassaction.jotform.com/',
        'name': 'Find Class Action (Jotform)',
        'json_file': 'findclassaction_urls.json'
    },
    'shamisgentile': {
        'url': 'https://shamisgentile.com/class-action-lawsuits/',
        'name': 'Shamis & Gentile',
        'json_file': 'shamisgentile_urls.json'
    },
    'toppefirm': {
        'url': 'https://www.toppefirm.com/sitemap.xml',
        'name': 'Toppe Law Firm',
        'json_file': 'toppefirm_urls.json'
    },
    'consumersprotectionlaw': {
        'url': 'https://consumersprotectionlaw.com/',
        'name': 'Consumers Protection Law',
        'json_file': 'consumersprotectionlaw_urls.json'
    },
    'consumerlegalaction': {
        'url': 'https://consumerlegalaction.com/',
        'name': 'Consumer Legal Action',
        'json_file': 'consumerlegalaction_urls.json'
    },
    'crosnerlegal': {
        'url': 'https://crosnerlegal.com/sitemap_index.xml',
        'name': 'Crosner Legal',
        'json_file': 'crosnerlegal_urls.json'
    },
    'edelson': {
        'url': 'https://edelson.com/',
        'name': 'Edelson PC',
        'json_file': 'edelson_urls.json'
    },
    'stopconsumerharm': {
        'url': 'https://www.stopconsumerharm.com/sitemap.xml',
        'name': 'Stop Consumer Harm',
        'json_file': 'stopconsumerharm_urls.json'
    },
    'eksm': {
        'url': 'https://eksm.com/',
        'name': 'EKSM Law',
        'json_file': 'eksm_urls.json'
    },
    'fmfpc': {
        'url': 'https://www.fmfpc.com/',
        'name': 'FMFPC',
        'json_file': 'fmfpc_urls.json'
    },
    'lanternlabaton': {
        'url': 'https://lantern.labaton.com/',
        'name': 'Lantern by Labaton',
        'json_file': 'lanternlabaton_urls.json'
    }
}

# Log file
LOG_FILE = LOGS_DIR / 'scraper.log'