"""
Base scraper class that all individual scrapers inherit from.
"""

import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config.settings import SCRAPING_CONFIG
from utils.logger import setup_logger
from utils.storage import URLStorage

logger = setup_logger(__name__)

# -----------------------------
# Defaults (matches your scrapers)
# -----------------------------
DEFAULT_CUTOFF_DATE = datetime(2026, 1, 1)

# -----------------------------
# Date parsing helpers
# -----------------------------
COMMON_DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%b %d, %Y",     # Jan 02, 2026
    "%B %d, %Y",     # January 02, 2026
    "%d %b %Y",      # 02 Jan 2026
    "%d %B %Y",      # 02 January 2026
    "%Y-%m-%dT%H:%M:%S",         # 2026-01-19T12:34:56
    "%Y-%m-%dT%H:%M:%S.%f",      # 2026-01-19T12:34:56.123456
]

# Conservative regex for date-like strings in surrounding text
DEFAULT_DATE_REGEX = re.compile(
    r"("
    r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b"  # 2026-01-19 or 2026/01/19
    r"|"
    r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b"  # 19-01-2026 or 19/01/2026
    r"|"
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}\b"  # Jan 19, 2026
    r")",
    re.IGNORECASE,
)


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    def __init__(self, source_url: str, source_name: str, json_filename: str):
        """
        Initialize the base scraper.

        Args:
            source_url: URL to scrape
            source_name: Name of the source
            json_filename: Name of JSON file to store URLs
        """
        self.source_url = source_url
        self.source_name = source_name
        self.storage = URLStorage(json_filename)

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": SCRAPING_CONFIG["user_agent"]})

        self.timeout = SCRAPING_CONFIG["request_timeout"]
        self.max_retries = SCRAPING_CONFIG["max_retries"]
        self.delay = SCRAPING_CONFIG["delay_between_requests"]

        # Default cutoff used by your scrapers (they don't pass it in)
        self.cutoff_date = DEFAULT_CUTOFF_DATE

    # -----------------------------
    # Networking
    # -----------------------------
    def get_page(self, url: str) -> requests.Response:
        """Get a web page with retry logic."""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching {url} (attempt {attempt + 1}/{self.max_retries})")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                time.sleep(self.delay)
                return response
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All retries failed for {url}")
                    raise
                time.sleep(self.delay * (attempt + 1))

    # -----------------------------
    # URL utilities
    # -----------------------------
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid (absolute URL with scheme and netloc)."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def normalize_url(self, url: str, base_url: str = None) -> str:
        """Normalize and convert relative URLs to absolute; strip fragments."""
        if base_url:
            url = urljoin(base_url, url)

        parsed = urlparse(url)
        return parsed._replace(fragment="").geturl()

    # -----------------------------
    # Date utilities
    # -----------------------------
    def parse_date(self, date_string: str) -> Optional[datetime]:
        """
        Parse a date string into a naive datetime.

        Handles:
        - ISO 8601 with timezone (we strip timezone part)
        - Many common formats
        """
        if not date_string:
            return None

        s = str(date_string).strip()
        if not s:
            return None

        # Normalize common ISO variants
        # 2026-01-19T10:30:00+00:00  -> 2026-01-19T10:30:00
        # 2026-01-19T10:30:00Z      -> 2026-01-19T10:30:00
        s = s.replace("Z", "")
        if "+" in s:
            s = s.split("+")[0].strip()

        # Try exact formats first
        for fmt in COMMON_DATE_FORMATS:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue

        # Try Python ISO parsing (covers many cases)
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None

    def _find_date_in_text(self, text: str, date_regex: Optional[re.Pattern] = None) -> Optional[datetime]:
        """Find a date-like substring inside text and parse it."""
        if not text:
            return None
        rx = date_regex or DEFAULT_DATE_REGEX
        m = rx.search(text)
        if not m:
            return None
        return self.parse_date(m.group(1))

    def filter_by_date(
        self,
        items: List[Dict[str, Any]],
        require_date: bool = False,
        cutoff_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter a list of {"url": ..., "date": datetime|None} items by cutoff date.

        This matches how your scrapers call it:
            self.filter_by_date(url_data, require_date=False)

        Args:
            items: list of dict items with keys: url, date
            require_date: True => exclude items with no date
                         False => include items with no date
            cutoff_date: date threshold; defaults to self.cutoff_date (Jan 1, 2026)

        Returns:
            Filtered list (same item dict objects)
        """
        cutoff = cutoff_date or self.cutoff_date
        out: List[Dict[str, Any]] = []

        for item in items:
            dt = item.get("date")

            if dt is None:
                if not require_date:
                    out.append(item)
                continue

            # If dt is a string (just in case), attempt parse
            if isinstance(dt, str):
                parsed = self.parse_date(dt)
                dt = parsed
                item["date"] = parsed

            if dt is not None and dt >= cutoff:
                out.append(item)

        return out

    # -----------------------------
    # Extraction: HTML
    # -----------------------------
    def extract_urls_from_html(self, html_content: str, base_url: str) -> Set[str]:
        """
        Extract all URLs from HTML content (no dates).
        Kept for backward compatibility.
        """
        soup = BeautifulSoup(html_content, "lxml")
        urls: Set[str] = set()

        for link in soup.find_all("a", href=True):
            url = self.normalize_url(link["href"], base_url)
            if self.is_valid_url(url):
                urls.add(url)

        return urls

    def extract_urls_from_html_with_dates(
        self,
        html_content: str,
        base_url: str,
        date_regex: Optional[re.Pattern] = None,
        max_context_chars: int = 300,
    ) -> List[Dict[str, Any]]:
        """
        Extract URLs from HTML content and associate best-effort dates.

        Returns:
            List[{"url": str, "date": Optional[datetime]}]
        """
        soup = BeautifulSoup(html_content, "lxml")
        results: List[Dict[str, Any]] = []

        seen: Set[str] = set()

        for link in soup.find_all("a", href=True):
            url = self.normalize_url(link["href"], base_url)
            if not self.is_valid_url(url):
                continue

            # Avoid duplicates early
            if url in seen:
                continue
            seen.add(url)

            dt = None

            # 1) Link text
            dt = self._find_date_in_text(link.get_text(" ", strip=True), date_regex=date_regex)

            # 2) Parent text (common: title + date in same row/card)
            if dt is None and link.parent:
                parent_text = link.parent.get_text(" ", strip=True)
                dt = self._find_date_in_text(parent_text, date_regex=date_regex)

            # 3) Context container text (bounded)
            if dt is None:
                context_node = link.find_parent(["article", "li", "tr", "div", "section"]) or link.parent
                if context_node:
                    context_text = context_node.get_text(" ", strip=True)
                    if len(context_text) > max_context_chars:
                        context_text = context_text[:max_context_chars]
                    dt = self._find_date_in_text(context_text, date_regex=date_regex)

            results.append({"url": url, "date": dt})

        return results

    # -----------------------------
    # Extraction: Sitemap (MUST return list for your scrapers)
    # -----------------------------
    def extract_urls_from_sitemap(self, xml_content: str) -> List[Dict[str, Any]]:
        """
        Extract URLs and <lastmod> dates from a sitemap.

        Returns:
            List[{"url": str, "date": Optional[datetime]}]

        Works for:
        - Normal sitemap: <url><loc>...</loc><lastmod>...</lastmod></url>
        - Sitemap index: <sitemap><loc>...</loc><lastmod>...</lastmod></sitemap>
          (Your Crosner scraper fetches each sitemap; this still works)
        """
        soup = BeautifulSoup(xml_content, "lxml-xml")
        results: List[Dict[str, Any]] = []
        seen: Set[str] = set()

        # Case 1: Standard <url> entries
        url_entries = soup.find_all("url")
        if url_entries:
            for u in url_entries:
                loc = u.find("loc")
                if not loc:
                    continue
                url = loc.get_text(strip=True)
                if not self.is_valid_url(url) or url in seen:
                    continue
                seen.add(url)

                lastmod = u.find("lastmod")
                dt = self.parse_date(lastmod.get_text(strip=True)) if lastmod else None
                results.append({"url": url, "date": dt})
            return results

        # Case 2: Sitemap index <sitemap> entries
        sitemap_entries = soup.find_all("sitemap")
        if sitemap_entries:
            for s in sitemap_entries:
                loc = s.find("loc")
                if not loc:
                    continue
                url = loc.get_text(strip=True)
                if not self.is_valid_url(url) or url in seen:
                    continue
                seen.add(url)

                lastmod = s.find("lastmod")
                dt = self.parse_date(lastmod.get_text(strip=True)) if lastmod else None
                results.append({"url": url, "date": dt})
            return results

        # Fallback: just grab all <loc>
        for loc in soup.find_all("loc"):
            url = loc.get_text(strip=True)
            if self.is_valid_url(url) and url not in seen:
                seen.add(url)
                results.append({"url": url, "date": None})

        return results

    # -----------------------------
    # Date extraction from a detail page
    # -----------------------------
    def extract_date_from_page(
        self,
        url: str,
        soup_or_selectors: Optional[Union[BeautifulSoup, List[str]]] = None,
        date_regex: Optional[re.Pattern] = None,
    ) -> Optional[datetime]:
        """
        Extract a published/updated date from a page.

        Compatible with your current usage:
            date = self.extract_date_from_page(item['url'], soup)

        Also supports:
            date = self.extract_date_from_page(url)                # fetch + parse
            date = self.extract_date_from_page(url, ["css..."])    # fetch + use selectors
        """
        selectors: Optional[List[str]] = None
        soup: Optional[BeautifulSoup] = None

        if isinstance(soup_or_selectors, BeautifulSoup):
            soup = soup_or_selectors
        elif isinstance(soup_or_selectors, list):
            selectors = soup_or_selectors

        # If soup not provided, fetch it
        if soup is None:
            resp = self.get_page(url)
            soup = BeautifulSoup(resp.text, "lxml")

        # 1) Common meta tags
        meta_candidates = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"property": "article:modified_time"}),
            ("meta", {"name": "date"}),
            ("meta", {"name": "pubdate"}),
            ("meta", {"name": "publishdate"}),
            ("meta", {"name": "timestamp"}),
            ("meta", {"itemprop": "datePublished"}),
            ("meta", {"itemprop": "dateModified"}),
        ]
        for tag, attrs in meta_candidates:
            node = soup.find(tag, attrs=attrs)
            if node and node.get("content"):
                dt = self.parse_date(node.get("content"))
                if dt:
                    return dt

        # 2) <time datetime="...">
        time_tag = soup.find("time", attrs={"datetime": True})
        if time_tag and time_tag.get("datetime"):
            dt = self.parse_date(time_tag.get("datetime"))
            if dt:
                return dt

        # 3) If selectors provided, try them
        if selectors:
            for sel in selectors:
                node = soup.select_one(sel)
                if not node:
                    continue

                # Try text
                dt = self._find_date_in_text(node.get_text(" ", strip=True), date_regex=date_regex)
                if dt:
                    return dt

                # Try common attrs
                for attr in ("datetime", "content", "data-date", "data-datetime"):
                    if node.has_attr(attr):
                        dt = self.parse_date(node.get(attr))
                        if dt:
                            return dt

        # 4) Fallback: regex scan on a bounded chunk of visible text
        text = soup.get_text(" ", strip=True)
        if text:
            text = text[:2500]
            return self._find_date_in_text(text, date_regex=date_regex)

        return None

    # -----------------------------
    # Abstract scrape
    # -----------------------------
    @abstractmethod
    def scrape(self) -> dict:
        """Perform the scraping operation. Must be implemented by subclasses."""
        raise NotImplementedError

    # -----------------------------
    # Runner
    # -----------------------------
    def run(self) -> dict:
        """Execute the scraping process with error handling."""
        logger.info(f"Starting scraper for {self.source_name}")
        logger.info(f"Source URL: {self.source_url}")

        try:
            result = self.scrape()
            logger.info(f"Scraping completed for {self.source_name}")
            return result
        except Exception as e:
            logger.error(f"Error scraping {self.source_name}: {e}", exc_info=True)
            return {
                "source_name": self.source_name,
                "status": "error",
                "error": str(e),
                "new_urls": 0,
                "total_urls": len(self.storage.get_existing_urls()),
                "scraped_urls": [],
            }
