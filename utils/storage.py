# """
# JSON storage utility for managing scraped URLs with dates.
# """
# import json
# from pathlib import Path
# from typing import List, Set, Dict, Optional
# from datetime import datetime
# from config.settings import DATA_DIR
# from utils.logger import setup_logger

# logger = setup_logger(__name__)


# class URLStorage:
#     """Manages storage and retrieval of scraped URLs with dates in JSON format."""
    
#     def __init__(self, json_filename: str):
#         """
#         Initialize URL storage.
        
#         Args:
#             json_filename: Name of the JSON file to store URLs
#         """
#         self.json_file = DATA_DIR / json_filename
#         self.data = self._load_data()
        
#     def _load_data(self) -> dict:
#         """
#         Load existing data from JSON file.
        
#         Returns:
#             dict: Existing data or empty structure
#         """
#         if self.json_file.exists():
#             try:
#                 with open(self.json_file, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     logger.info(f"Loaded {len(data.get('entries', []))} existing entries from {self.json_file.name}")
#                     return data
#             except json.JSONDecodeError as e:
#                 logger.error(f"Error decoding JSON from {self.json_file}: {e}")
#                 return self._create_empty_structure()
#         else:
#             logger.info(f"No existing file found: {self.json_file.name}. Creating new.")
#             return self._create_empty_structure()
    
#     def _create_empty_structure(self) -> dict:
#         """
#         Create an empty data structure.
        
#         Returns:
#             dict: Empty data structure
#         """
#         return {
#             'source': '',
#             'last_updated': '',
#             'total_entries': 0,
#             'cutoff_date': '2026-01-01',
#             'entries': []  # List of {url, date, scraped_at}
#         }
    
#     def get_existing_urls(self) -> Set[str]:
#         """
#         Get a set of existing URLs for fast duplicate checking.
        
#         Returns:
#             Set[str]: Set of existing URLs
#         """
#         return {entry['url'] for entry in self.data.get('entries', [])}
    
#     def add_urls_with_dates(self, url_date_list: List[Dict[str, str]], source_name: str) -> int:
#         """
#         Add new URLs with their dates to storage, avoiding duplicates.
        
#         Args:
#             url_date_list: List of dicts with 'url' and 'date' keys
#             source_name: Name of the source
            
#         Returns:
#             int: Number of new URLs added
#         """
#         existing_urls = self.get_existing_urls()
#         new_entries = []
        
#         for item in url_date_list:
#             url = item.get('url')
#             date = item.get('date', '')
            
#             if url and url not in existing_urls:
#                 new_entries.append({
#                     'url': url,
#                     'date': date,
#                     'scraped_at': datetime.now().isoformat()
#                 })
#                 existing_urls.add(url)  # Prevent duplicates within same batch
        
#         if new_entries:
#             self.data['entries'].extend(new_entries)
#             self.data['source'] = source_name
#             self.data['last_updated'] = datetime.now().isoformat()
#             self.data['total_entries'] = len(self.data['entries'])
            
#             self._save_data()
#             logger.info(f"Added {len(new_entries)} new entries to {self.json_file.name}")
#         else:
#             logger.info(f"No new entries to add to {self.json_file.name}")
        
#         return len(new_entries)
    
#     def add_urls(self, urls: List[str], source_name: str) -> int:
#         """
#         Add URLs without dates (backward compatibility).
        
#         Args:
#             urls: List of URLs to add
#             source_name: Name of the source
            
#         Returns:
#             int: Number of new URLs added
#         """
#         url_date_list = [{'url': url, 'date': ''} for url in urls]
#         return self.add_urls_with_dates(url_date_list, source_name)
    
#     def _save_data(self):
#         """Save data to JSON file."""
#         try:
#             with open(self.json_file, 'w', encoding='utf-8') as f:
#                 json.dump(self.data, f, indent=2, ensure_ascii=False)
#             logger.info(f"Data saved to {self.json_file.name}")
#         except Exception as e:
#             logger.error(f"Error saving data to {self.json_file}: {e}")
    
#     def get_stats(self) -> dict:
#         """
#         Get statistics about stored URLs.
        
#         Returns:
#             dict: Statistics including total URLs and last update time
#         """
#         entries = self.data.get('entries', [])
#         entries_with_dates = [e for e in entries if e.get('date')]
        
#         return {
#             'source': self.data.get('source', 'Unknown'),
#             'total_entries': len(entries),
#             'entries_with_dates': len(entries_with_dates),
#             'entries_without_dates': len(entries) - len(entries_with_dates),
#             'last_updated': self.data.get('last_updated', 'Never'),
#             'cutoff_date': self.data.get('cutoff_date', '2026-01-01'),
#             'json_file': self.json_file.name
#         }
    
#     def get_urls_after_date(self, cutoff_date: str = '2026-01-01') -> List[str]:
#         """
#         Get URLs with dates after the cutoff.
        
#         Args:
#             cutoff_date: ISO format date string (YYYY-MM-DD)
            
#         Returns:
#             List[str]: URLs after cutoff date
#         """
#         urls = []
#         for entry in self.data.get('entries', []):
#             date_str = entry.get('date', '')
#             if date_str and date_str >= cutoff_date:
#                 urls.append(entry['url'])
#         return urls

































"""
JSON storage utility for managing scraped URLs with dates.
"""
import json
from pathlib import Path
from typing import List, Set, Dict, Optional, Tuple, Any
from datetime import datetime
from config.settings import DATA_DIR
from utils.logger import setup_logger

logger = setup_logger(__name__)


class URLStorage:
    """Manages storage and retrieval of scraped URLs with dates in JSON format."""

    def __init__(self, json_filename: str):
        self.json_file = DATA_DIR / json_filename
        self.data = self._load_data()

    def _load_data(self) -> dict:
        if self.json_file.exists():
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                logger.info(
                    f"Loaded {len(data.get('entries', []))} existing entries from {self.json_file.name}"
                )
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from {self.json_file}: {e}")
                return self._create_empty_structure()
        else:
            logger.info(f"No existing file found: {self.json_file.name}. Creating new.")
            return self._create_empty_structure()

    def _create_empty_structure(self) -> dict:
        return {
            "source": "",
            "last_updated": "",
            "total_entries": 0,
            "cutoff_date": "2026-01-01",
            "entries": [],  # List of {url, date, scraped_at}
        }

    def get_existing_urls(self) -> Set[str]:
        return {entry["url"] for entry in self.data.get("entries", []) if entry.get("url")}

    def _normalize_date(self, value: Any) -> str:
        """
        Normalize date values to a JSON-safe ISO string.
        - datetime -> ISO string
        - None/"" -> ""
        - other -> str(value)
        """
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.isoformat()
        s = str(value).strip()
        return s

    def add_urls_with_dates(
        self,
        url_date_list: List[Dict[str, Any]],
        source_name: str
    ) -> Tuple[int, List[str]]:
        """
        Add new URLs with their dates to storage, avoiding duplicates.

        Returns:
            (count_added, new_urls_added_list)
        """
        existing_urls = self.get_existing_urls()
        new_entries = []
        new_urls = []

        for item in url_date_list:
            url = (item.get("url") or "").strip()
            if not url:
                continue

            if url in existing_urls:
                continue

            date_val = self._normalize_date(item.get("date"))
            new_entries.append({
                "url": url,
                "date": date_val,
                "scraped_at": datetime.now().isoformat(),
            })
            new_urls.append(url)
            existing_urls.add(url)  # prevent duplicates within same batch

        # Always update metadata (even if no new URLs)
        self.data["source"] = source_name
        self.data["last_updated"] = datetime.now().isoformat()

        if new_entries:
            self.data["entries"].extend(new_entries)

        self.data["total_entries"] = len(self.data["entries"])
        self._save_data()

        logger.info(f"Added {len(new_entries)} new entries to {self.json_file.name}")
        return len(new_entries), new_urls

    def add_urls(self, urls: List[str], source_name: str) -> Tuple[int, List[str]]:
        url_date_list = [{"url": url, "date": ""} for url in urls]
        return self.add_urls_with_dates(url_date_list, source_name)

    def _save_data(self):
        try:
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {self.json_file.name}")
        except Exception as e:
            logger.error(f"Error saving data to {self.json_file}: {e}")

    def get_stats(self) -> dict:
        entries = self.data.get("entries", [])
        entries_with_dates = [e for e in entries if e.get("date")]
        return {
            "source": self.data.get("source", "Unknown"),
            "total_entries": len(entries),
            "entries_with_dates": len(entries_with_dates),
            "entries_without_dates": len(entries) - len(entries_with_dates),
            "last_updated": self.data.get("last_updated", "Never"),
            "cutoff_date": self.data.get("cutoff_date", "2026-01-01"),
            "json_file": self.json_file.name,
        }
