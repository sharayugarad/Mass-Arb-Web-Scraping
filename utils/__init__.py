"""Utilities package for class action scraper."""
from .logger import setup_logger
from .storage import URLStorage
from .email_sender import EmailSender

__all__ = ['setup_logger', 'URLStorage', 'EmailSender']