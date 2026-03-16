"""
Email utility for sending scraping results.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List
from config.settings import EMAIL_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailSender:
    """Handles sending email notifications with scraping results."""
    
    def __init__(self):
        """Initialize email sender with configuration."""
        self.smtp_server = EMAIL_CONFIG['smtp_server']
        self.smtp_port = EMAIL_CONFIG['smtp_port']
        self.use_ssl = EMAIL_CONFIG['use_ssl']
        self.sender_email = EMAIL_CONFIG['sender_email']
        self.sender_password = EMAIL_CONFIG['sender_password']
        self.receiver_emails = EMAIL_CONFIG['receiver_emails']
        
    def _validate_config(self) -> bool:
        """
        Validate email configuration.
        
        Returns:
            bool: True if configuration is valid
        """
        if not all([self.sender_email, self.sender_password]):
            logger.error("Email configuration incomplete. Sender email or password missing.")
            return False
        
        if not self.receiver_emails or len(self.receiver_emails) == 0:
            logger.error("No receiver emails configured. Set RECEIVER_EMAILS in your .env file.")
            return False
            
        return True
    
    def create_email_body(self, scraping_results: Dict[str, Dict]) -> str:
        """
        Create HTML email body with scraping results.
        
        Args:
            scraping_results: Dictionary containing scraping results for each source
            
        Returns:
            str: HTML formatted email body
        """
        total_new_urls = sum(result.get('new_urls', 0) for result in scraping_results.values())
        total_existing_urls = sum(result.get('total_urls', 0) for result in scraping_results.values())
        
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .summary {{
                    background-color: #f4f4f4;
                    padding: 15px;
                    margin: 20px 0;
                    border-left: 4px solid #4CAF50;
                }}
                .source-section {{
                    margin: 20px 0;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                .source-name {{
                    color: #4CAF50;
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .stats {{
                    margin: 10px 0;
                }}
                .new-urls {{
                    background-color: #e8f5e9;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 3px;
                }}
                .url-list {{
                    list-style-type: none;
                    padding: 0;
                }}
                .url-list li {{
                    padding: 5px;
                    margin: 5px 0;
                    background-color: #fff;
                    border-left: 3px solid #4CAF50;
                    padding-left: 10px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding: 15px;
                    background-color: #f4f4f4;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }}
                .no-new-urls {{
                    color: #ff9800;
                    font-style: italic;
                }}
                .error {{
                    color: #f44336;
                    background-color: #ffebee;
                    padding: 10px;
                    border-radius: 3px;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Daily Mass Arbitration Links</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Total New URLs Scraped:</strong> {total_new_urls}</p>
                <p><strong>Total URLs in Database:</strong> {total_existing_urls}</p>
                <p><strong>Sources Scraped:</strong> {len(scraping_results)}</p>
            </div>
        """
        
        # Add details for each source
        for source_key, result in scraping_results.items():
            source_name = result.get('source_name', source_key)
            new_urls = result.get('new_urls', 0)
            total_urls = result.get('total_urls', 0)
            scraped_urls = result.get('scraped_urls', [])
            status = result.get('status', 'unknown')
            error = result.get('error', '')
            
            html += f"""
            <div class="source-section">
                <div class="source-name">{source_name}</div>
                <div class="stats">
                    <p><strong>Status:</strong> {'✓ ' if status == 'success' else '✗ '}{status.upper()}</p>
                    <p><strong>New URLs Found:</strong> {new_urls}</p>
                    <p><strong>Total URLs in Storage:</strong> {total_urls}</p>
            """
            
            if error:
                html += f'<div class="error"><strong>Error:</strong> {error}</div>'
            
            html += "</div>"
            
            if scraped_urls:
                html += f"""
                <div class="new-urls">
                    <strong>Newly Scraped URLs ({len(scraped_urls)}):</strong>
                    <ul class="url-list">
                """
                
                # display_urls = scraped_urls
                for url in scraped_urls:
                    html += f'<li><a href="{url}">{url}</a></li>'
                
                html += """
                    </ul>
                </div>
                """
            else:
                html += '<p class="no-new-urls">No new URLs found for this source.</p>'
            
            html += "</div>"
        
        html += """
            <div class="footer">
                <p>This is an automated report from the Class Action Scraper.</p>
                <p>All URLs are stored in their respective JSON files in the data directory.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_email(self, scraping_results: Dict[str, Dict]) -> bool:
        """
        Send email with scraping results to all configured recipients.
        
        Args:
            scraping_results: Dictionary containing scraping results
            
        Returns:
            bool: True if email sent successfully to all recipients
        """
        if not self._validate_config():
            return False
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = f'Daily Mass Arbitration Links'
            message['From'] = self.sender_email
            message['To'] = ', '.join(self.receiver_emails)  # Multiple recipients
            
            # Create email body
            html_body = self.create_email_body(scraping_results)
            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)
            
            # Send email
            logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            
            if self.use_ssl:
                # Use SSL connection
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)
            else:
                # Use TLS connection (default for port 587)
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)
            
            logger.info(f"Email sent successfully to {len(self.receiver_emails)} recipients:")
            for email in self.receiver_emails:
                logger.info(f"  - {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False