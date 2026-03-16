"""
Date utility functions for extracting and comparing dates from web pages.
"""
import re
from datetime import datetime
from typing import Optional, List
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Cutoff date: January 1st, 2026
CUTOFF_DATE = datetime(2026, 1, 17)


def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse a date string using multiple common formats.
    
    Args:
        date_string: String containing a date
        
    Returns:
        datetime object if parsing successful, None otherwise
    """
    if not date_string:
        return None
    
    # Clean the date string
    date_string = date_string.strip()
    
    # Common date formats to try
    date_formats = [
        '%Y-%m-%d',           # 2026-01-15
        '%m/%d/%Y',           # 01/15/2026
        '%d/%m/%Y',           # 15/01/2026
        '%B %d, %Y',          # January 15, 2026
        '%b %d, %Y',          # Jan 15, 2026
        '%Y/%m/%d',           # 2026/01/15
        '%d-%m-%Y',           # 15-01-2026
        '%m-%d-%Y',           # 01-15-2026
        '%Y.%m.%d',           # 2026.01.15
        '%d.%m.%Y',           # 15.01.2026
        '%B %d %Y',           # January 15 2026
        '%b %d %Y',           # Jan 15 2026
        '%d %B %Y',           # 15 January 2026
        '%d %b %Y',           # 15 Jan 2026
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    # Try to extract year-month-day pattern
    patterns = [
        r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        r'(\d{2})/(\d{2})/(\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
        r'(\d{4})/(\d{2})/(\d{2})',  # YYYY/MM/DD
    ]
    
    for pattern in patterns:
        match = re.search(pattern, date_string)
        if match:
            try:
                # Try YYYY-MM-DD format
                year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                if year > 1000:  # Looks like YYYY-MM-DD
                    return datetime(year, month, day)
                else:  # Might be MM/DD/YYYY or DD/MM/YYYY
                    # Try MM/DD/YYYY first (US format)
                    try:
                        return datetime(int(match.group(3)), int(match.group(1)), int(match.group(2)))
                    except ValueError:
                        # Try DD/MM/YYYY
                        return datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))
            except (ValueError, IndexError):
                continue
    
    logger.debug(f"Could not parse date: {date_string}")
    return None


def is_after_cutoff(date_obj: Optional[datetime]) -> bool:
    """
    Check if a date is after the cutoff date (Jan 1, 2026).
    
    Args:
        date_obj: datetime object to check
        
    Returns:
        bool: True if date is after cutoff, False otherwise
    """
    if date_obj is None:
        return False
    return date_obj >= CUTOFF_DATE


def extract_dates_from_text(text: str) -> List[datetime]:
    """
    Extract all possible dates from text.
    
    Args:
        text: Text to search for dates
        
    Returns:
        List of datetime objects found
    """
    dates = []
    
    # Look for various date patterns in text
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',           # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',           # MM/DD/YYYY or DD/MM/YYYY
        r'\d{4}/\d{2}/\d{2}',           # YYYY/MM/DD
        r'\w+ \d{1,2},? \d{4}',         # Month DD, YYYY
        r'\d{1,2} \w+ \d{4}',           # DD Month YYYY
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            parsed = parse_date(match)
            if parsed:
                dates.append(parsed)
    
    return dates


def get_most_recent_date(dates: List[datetime]) -> Optional[datetime]:
    """
    Get the most recent date from a list.
    
    Args:
        dates: List of datetime objects
        
    Returns:
        Most recent datetime or None if list is empty
    """
    if not dates:
        return None
    return max(dates)


def format_date(date_obj: Optional[datetime]) -> str:
    """
    Format a datetime object as ISO string.
    
    Args:
        date_obj: datetime object
        
    Returns:
        ISO formatted string or empty string if None
    """
    if date_obj is None:
        return ''
    return date_obj.strftime('%Y-%m-%d')