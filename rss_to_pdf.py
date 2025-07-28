#!/usr/bin/env python3
"""
RSS to PDF Converter
Downloads articles from RSS feeds and converts them to a well-formatted PDF for reading.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import html2text
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import argparse
import sys
import os
from datetime import datetime
import time
from io import BytesIO
from PIL import Image as PILImage


class RSSToPDFConverter:
    def __init__(self, output_file="rss_articles.pdf"):
        """Initialize the RSS to PDF converter."""
        self.output_file = output_file
        
        # Register Ubuntu fonts
        try:
            pdfmetrics.registerFont(TTFont('Ubuntu', 'fonts/Ubuntu-Regular.ttf'))
            pdfmetrics.registerFont(TTFont('Ubuntu-Bold', 'fonts/Ubuntu-Bold.ttf'))
            pdfmetrics.registerFont(TTFont('Ubuntu-Italic', 'fonts/Ubuntu-Italic.ttf'))
            pdfmetrics.registerFont(TTFont('Ubuntu-BoldItalic', 'fonts/Ubuntu-BoldItalic.ttf'))
            self.ubuntu_fonts_available = True
        except Exception as e:
            print(f"Warning: Could not load Ubuntu fonts: {e}")
            print("Falling back to default fonts...")
            self.ubuntu_fonts_available = False
        
        # Configure html2text
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_emphasis = True
        self.h2t.ignore_tables = True
        self.h2t.ignore_links = False  # Keep links for images
        self.h2t.escape_snob = False
        self.h2t.body_width = 0  # No line wrapping
        self.h2t.unicode_snob = True
        self.h2t.ignore_images = False  # Include images
        self.h2t.ignore_emphasis = True
        self.h2t.ignore_tables = True
        
        # Setup styles
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Setup custom styles optimized for e-ink devices."""
        self.styles = getSampleStyleSheet()
        
        # Set font names based on availability
        title_font = 'Ubuntu-Bold' if self.ubuntu_fonts_available else 'Helvetica-Bold'
        content_font = 'Ubuntu' if self.ubuntu_fonts_available else 'Helvetica'
        subtitle_font = 'Ubuntu-Bold' if self.ubuntu_fonts_available else 'Helvetica-Bold'
        section_font = 'Ubuntu-Bold' if self.ubuntu_fonts_available else 'Helvetica-Bold'
        
        # E-ink optimized styles - high contrast, clean, minimal
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=20,
            spaceBefore=30,
            textColor=black,
            alignment=TA_CENTER,
            fontName=title_font,
            leading=28,
            borderWidth=0,
            borderColor=black,
            borderPadding=0
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=16,
            spaceBefore=24,
            textColor=black,
            alignment=TA_LEFT,
            fontName=subtitle_font,
            leading=22,
            borderWidth=0,
            borderColor=black,
            borderPadding=0
        )
        
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading3'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=black,
            alignment=TA_LEFT,
            fontName=section_font,
            leading=20,
            borderWidth=0,
            borderColor=black,
            borderPadding=0
        )
        
        self.meta_style = ParagraphStyle(
            'CustomMeta',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            spaceBefore=0,
            textColor=black,
            alignment=TA_JUSTIFY,
            fontName=content_font,
            leading=14,
            borderWidth=0,
            borderColor=black,
            borderPadding=0
        )
        
        self.content_style = ParagraphStyle(
            'CustomContent',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=0,
            textColor=black,
            alignment=TA_JUSTIFY,
            fontName=content_font,
            leading=16,
            borderWidth=0,
            borderColor=black,
            borderPadding=0,
            leftIndent=0,
            rightIndent=0
        )
        
        self.link_style = ParagraphStyle(
            'CustomLink',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=4,
            spaceBefore=0,
            textColor=black,
            alignment=TA_JUSTIFY,
            fontName=content_font,
            leading=14,
            borderWidth=0,
            borderColor=black,
            borderPadding=0
        )
        
        self.quote_style = ParagraphStyle(
            'CustomQuote',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            spaceBefore=16,
            textColor=black,
            alignment=TA_JUSTIFY,
            fontName=content_font,
            leading=14,
            leftIndent=20,
            rightIndent=20,
            borderWidth=0,
            borderColor=black,
            borderPadding=0
        )
        
        self.list_style = ParagraphStyle(
            'CustomList',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=4,
            spaceBefore=0,
            textColor=black,
            alignment=TA_JUSTIFY,
            fontName=content_font,
            leading=16,
            leftIndent=20,
            borderWidth=0,
            borderColor=black,
            borderPadding=0
        )
        
        self.code_style = ParagraphStyle(
            'CustomCode',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            spaceBefore=12,
            textColor=black,
            alignment=TA_LEFT,
            fontName='Courier' if self.ubuntu_fonts_available else 'Courier',
            leading=12,
            leftIndent=20,
            rightIndent=20,
            borderWidth=1,
            borderColor=black,
            borderPadding=8,
            backColor=white
        )
        
        self.image_style = ParagraphStyle(
            'CustomImage',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=16,
            spaceBefore=16,
            textColor=black,
            alignment=TA_CENTER,
            fontName=content_font,
            leading=12,
            borderWidth=0,
            borderColor=black,
            borderPadding=0
        )

    def validate_rss_feed(self, feed_url):
        """Validate RSS feed URL and check if it's accessible and valid."""
        try:
            print(f"🔍 Validating RSS feed: {feed_url}")
            
            # Check if URL is accessible
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache'
            }
            
            # First, try to get the feed with requests to check accessibility
            response = requests.get(feed_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(xml_type in content_type for xml_type in ['xml', 'rss', 'atom']):
                print(f"⚠️  Warning: Content type '{content_type}' may not be RSS/Atom")
            
            # Parse with feedparser to validate structure
            feed = feedparser.parse(feed_url)
            
            # Check for parsing errors
            if feed.bozo:
                print(f"⚠️  Warning: Feed may be malformed (bozo flag set)")
                if hasattr(feed, 'bozo_exception'):
                    print(f"   Exception: {feed.bozo_exception}")
            
            # Check if feed has entries
            if not feed.entries:
                print(f"❌ Error: No entries found in feed")
                return False, "No entries found in feed"
            
            # Check feed metadata
            feed_title = feed.feed.get('title', 'Unknown')
            feed_description = feed.feed.get('description', 'No description')
            entry_count = len(feed.entries)
            
            print(f"✅ RSS feed validation successful!")
            print(f"   Title: {feed_title}")
            print(f"   Description: {feed_description}")
            print(f"   Entries found: {entry_count}")
            
            # Check for common RSS feed issues
            issues = []
            
            # Check if entries have required fields
            missing_titles = sum(1 for entry in feed.entries if not getattr(entry, 'title', None))
            missing_links = sum(1 for entry in feed.entries if not getattr(entry, 'link', None))
            
            if missing_titles > 0:
                issues.append(f"{missing_titles} entries missing titles")
            if missing_links > 0:
                issues.append(f"{missing_links} entries missing links")
            
            # Check for recent entries (within last 30 days)
            recent_entries = 0
            for entry in feed.entries[:10]:  # Check first 10 entries
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    entry_date = datetime(*entry.published_parsed[:6])
                    if (datetime.now() - entry_date).days <= 30:
                        recent_entries += 1
            
            if recent_entries == 0:
                issues.append("No recent entries (within 30 days)")
            else:
                print(f"   Recent entries (30 days): {recent_entries}")
            
            if issues:
                print(f"⚠️  Potential issues: {', '.join(issues)}")
            else:
                print(f"✅ Feed appears healthy with no major issues")
            
            return True, f"Valid RSS feed with {entry_count} entries"
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error accessing RSS feed: {e}")
            return False, f"Network error: {e}"
        except Exception as e:
            print(f"❌ Error validating RSS feed: {e}")
            return False, f"Validation error: {e}"

    def fetch_rss_feed(self, feed_url):
        """Fetch and parse RSS feed with automatic validation."""
        try:
            # First validate the RSS feed
            is_valid, validation_message = self.validate_rss_feed(feed_url)
            
            if not is_valid:
                print(f"❌ RSS feed validation failed: {validation_message}")
                return []
            
            print(f"📥 Fetching RSS feed from: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                print(f"⚠️  Warning: Feed may be malformed")
            
            if not feed.entries:
                print(f"❌ Error: No entries found in feed")
                return []
            
            print(f"✅ Found {len(feed.entries)} entries in feed")
            
            articles = []
            for entry in feed.entries:
                title = getattr(entry, 'title', 'No title')
                link = getattr(entry, 'link', '')
                published = getattr(entry, 'published', '')
                author = getattr(entry, 'author', 'Unknown')
                
                print(f"  📄 Article: {title}")
                print(f"    🔗 URL: {link}")
                
                articles.append({
                    'title': title,
                    'link': link,
                    'published': published,
                    'author': author
                })
            
            return articles
            
        except Exception as e:
            print(f"❌ Error fetching RSS feed: {e}")
            return []

    def clean_text(self, text):
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Replace HTML entities
        text = text.replace('&quot;', '"')
        text = text.replace('&ldquo;', '"')
        text = text.replace('&rdquo;', '"')
        text = text.replace('&lsquo;', "'")
        text = text.replace('&rsquo;', "'")
        text = text.replace('&apos;', "'")
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&nbsp;', ' ')
        
        # Remove escaped backslashes
        text = text.replace('\\"', '"')
        text = text.replace("\\'", "'")
        text = text.replace('\\\\', '\\')
        
        # Remove other escaped characters
        text = text.replace('\\.', '.')
        text = text.replace('\\,', ',')
        text = text.replace('\\!', '!')
        text = text.replace('\\?', '?')
        
        # Remove any remaining backslashes that might cause rendering issues
        text = text.replace('\\', '')
        
        # Remove any non-printable characters that might cause black boxes
        text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
        
        # Remove random exclamation marks and other artifacts
        text = re.sub(r'\s+!+\s+', ' ', text)  # Remove isolated exclamation marks
        text = re.sub(r'!{2,}', '!', text)  # Reduce multiple exclamation marks to single
        text = re.sub(r'\s+[^\w\s\.\,\!\?\-\(\)]+\s+', ' ', text)  # Remove other random characters
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text

    def clean_html_for_pdf(self, html_content):
        """Clean HTML content to be safe for ReportLab PDF generation."""
        if not html_content:
            return ""
        
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(["script", "style", "noscript"]):
                element.decompose()
            
            # Remove problematic attributes from all tags
            for tag in soup.find_all(True):
                # Keep only safe attributes for PDF
                safe_attrs = ['href', 'src', 'alt', 'title']
                attrs_to_remove = []
                for attr in tag.attrs:
                    if attr not in safe_attrs:
                        attrs_to_remove.append(attr)
                
                for attr in attrs_to_remove:
                    del tag[attr]
            
            # Convert to string and clean up
            cleaned_html = str(soup)
            
            # Remove any remaining problematic HTML patterns
            cleaned_html = re.sub(r'<[^>]*class\s*=\s*["\'][^"\']*["\'][^>]*>', '', cleaned_html)
            cleaned_html = re.sub(r'<[^>]*style\s*=\s*["\'][^"\']*["\'][^>]*>', '', cleaned_html)
            cleaned_html = re.sub(r'<[^>]*id\s*=\s*["\'][^"\']*["\'][^>]*>', '', cleaned_html)
            
            # Convert to markdown
            markdown_content = self.h2t.handle(cleaned_html)
            
            # Clean up the markdown content
            cleaned_content = self.clean_markdown_content(markdown_content)
            
            return cleaned_content
            
        except Exception as e:
            print(f"Error cleaning HTML: {e}")
            # Fallback: strip all HTML tags
            text_only = re.sub(r'<[^>]+>', '', html_content)
            return self.clean_text(text_only)
    
    def clean_markdown_content(self, markdown_content):
        """Clean markdown content by removing raw syntax and fixing characters."""
        if not markdown_content:
            return ""
        
        # Remove raw markdown syntax
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', markdown_content)  # Bold
        content = re.sub(r'\*(.*?)\*', r'\1', content)  # Italic
        content = re.sub(r'_(.*?)_', r'\1', content)  # Underline
        content = re.sub(r'`(.*?)`', r'\1', content)  # Inline code
        content = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', content)  # Links
        content = re.sub(r'^[-*•]\s*', '', content, flags=re.MULTILINE)  # List markers
        content = re.sub(r'^\d+\.\s*', '', content, flags=re.MULTILINE)  # Numbered lists
        content = re.sub(r'^>\s*', '', content, flags=re.MULTILINE)  # Blockquotes
        
        # Handle code blocks - preserve them but clean up formatting
        content = re.sub(r'```(\w+)?\n(.*?)```', r'CODE BLOCK:\n\2', content, flags=re.DOTALL)
        
        # IMPORTANT: Preserve images - don't remove them!
        # content = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'[Image: \1]', content)
        # content = re.sub(r'<img[^>]*>', r'[Image]', content)
        
        # Clean up any remaining escaped characters
        content = content.replace('\\"', '"')
        content = content.replace("\\'", "'")
        content = content.replace('\\\\', '\\')
        content = content.replace('\\.', '.')
        content = content.replace('\\,', ',')
        content = content.replace('\\!', '!')
        content = content.replace('\\?', '?')
        
        # Remove any remaining backslashes that might cause rendering issues
        content = content.replace('\\', '')
        
        # Remove any non-printable characters that might cause black boxes
        content = re.sub(r'[^\x20-\x7E\n\t]', '', content)
        
        # Remove random exclamation marks that might be artifacts
        content = re.sub(r'\s+!+\s+', ' ', content)  # Remove isolated exclamation marks
        content = re.sub(r'!{2,}', '!', content)  # Reduce multiple exclamation marks to single
        
        # Normalize whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        content = content.strip()
        
        return content

    def is_content_image(self, src, alt):
        """Determine if an image is actual content vs profile/avatar."""
        # Skip images that are likely profile photos, avatars, or UI elements
        skip_patterns = [
            'avatar', 'profile', 'user', 'author', 'writer', 'contributor',
            'icon', 'logo', 'button', 'badge', 'emoji', 'social',
            'thumb', 'thumbnail', 'small', 'tiny', 'mini',
            '36x36', '48x48', '64x64', '128x128',  # Common avatar sizes
            'w_36', 'w_48', 'w_64', 'h_36', 'h_48', 'h_64',  # CDN size indicators
            'substack.com/@',  # Substack profile URLs
            'bucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com'  # Substack avatar bucket
        ]
        
        # Check if URL or alt text contains skip patterns
        src_lower = src.lower()
        alt_lower = alt.lower()
        
        for pattern in skip_patterns:
            if pattern in src_lower or pattern in alt_lower:
                return False
        
        # Check for small image dimensions in URL
        if any(size in src for size in ['w_36', 'w_48', 'w_64', 'h_36', 'h_48', 'h_64']):
            return False
        
        # Check if it's a Substack profile image
        if 'substack.com/@' in src or 'bucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com' in src:
            return False
        
        # Prefer images with meaningful alt text or larger dimensions
        if alt and len(alt) > 3:  # Has meaningful alt text
            return True
        
        # Check for larger image dimensions (likely content images)
        if any(size in src for size in ['w_520', 'w_1456', 'w_1024', 'w_800', 'h_272', 'h_1369', 'h_1100']):
            return True
        
        # Default to including if no clear indicators of being non-content
        return True

    def extract_base_image_url(self, url):
        """Extract the base URL from an image URL, removing size parameters."""
        if not url:
            return ""
        
        # For Substack CDN URLs, extract the original URL
        if 'substackcdn.com' in url:
            # The URLs are malformed, so we need to extract the image ID
            # Look for the image ID pattern: ab82ead4-9593-43b2-932c-cfd7ddf464fc_1376x864.png
            image_id_match = re.search(r'([a-f0-9-]+)_\d+x\d+\.(png|jpg|jpeg)', url)
            if image_id_match:
                image_id = image_id_match.group(1)
                return f"image_id_{image_id}"  # Use image ID as base identifier
            
            # Fallback: try to extract any unique identifier
            unique_match = re.search(r'([a-f0-9-]{20,})', url)
            if unique_match:
                return f"unique_{unique_match.group(1)}"
        
        # For other URLs, remove size parameters
        url = re.sub(r'[?&]w=\d+', '', url)
        url = re.sub(r'[?&]h=\d+', '', url)
        url = re.sub(r'[?&]c_limit', '', url)
        url = re.sub(r'[?&]c_fill', '', url)
        return url

    def extract_article_content(self, article_url):
        """Extract article content from URL."""
        try:
            # Clean the URL by removing fragments
            clean_url = article_url.split('#')[0]
            print(f"  Extracting content from: {clean_url}")
            
            # Enhanced headers to avoid 403 errors
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            response = requests.get(clean_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Try to detect encoding
            if response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            
            # Try different content selectors for various blog platforms
            content_selectors = [
                'article',
                '.post-content',
                '.entry-content',
                '.content',
                '.post-body',
                'main',
                '.main-content',
                '#content',
                '.article-content',
                '.post',
                '.entry',
                '.blog-post',
                '.post-text',
                '.entry-text',
                '.post-body',
                '.content-body',
                '.article-body',
                '.post-content',
                '.entry-content',
                '.blog-entry',
                '.post-entry',
                '#primary'  # Simon Willison's blog
            ]
            
            content = None
            used_selector = None
            content_elem = None
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove navigation, header, footer, sidebar elements
                    for elem in content_elem.find_all(['nav', 'header', 'footer', 'aside']):
                        elem.decompose()
                    
                    # Remove common non-content classes
                    for elem in content_elem.find_all(class_=re.compile(r'sidebar|navigation|menu|nav|ad|advertisement|social|share|comment|footer|header')):
                        elem.decompose()
                    
                    content = content_elem.get_text(separator='\n', strip=True)
                    if len(content) > 500:  # Lower threshold for shorter posts
                        used_selector = selector
                        break
            
            # If no specific content area found, try to extract from the entire body
            if not content:
                body = soup.find('body')
                if body:
                    # Remove navigation elements from body
                    for elem in body.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style']):
                        elem.decompose()
                    
                    content = body.get_text(separator='\n', strip=True)
                    used_selector = 'body'
                    content_elem = body
            
            if content:
                print(f"  Found content using selector: {used_selector}")
                print(f"  Content area found, size: {len(content)} characters")
                
                # Extract images from the content area
                self.current_article_images = []
                seen_urls = set()
                
                if content_elem:
                    images = content_elem.find_all('img')
                    print(f"  Found {len(images)} images in HTML")
                    
                    for img in images:
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        
                        if src and src.startswith('http'):
                            # Check if this is a content image
                            if self.is_content_image(src, alt):
                                base_url = self.extract_base_image_url(src)
                                if base_url not in seen_urls:
                                    seen_urls.add(base_url)
                                    self.current_article_images.append((src, alt))
                                    print(f"    Added image: {alt} -> {src}")
                
                # Structure the content
                content = self.structure_content(content)
                
                # Convert to markdown
                markdown_content = self.h2t.handle(str(content_elem) if content_elem else content)
                
                # Clean the markdown content
                cleaned_content = self.clean_markdown_content(markdown_content)
                
                return cleaned_content
            else:
                print("  No content found with any selector")
                return None
                
        except Exception as e:
            print(f"  Error extracting content: {e}")
            return None
    
    def structure_content(self, content):
        """Structure the content by filtering out very short paragraphs."""
        if not content:
            return ""
        
        paragraphs = content.split('\n\n')
        structured_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph and len(paragraph) > 20:  # Keep paragraphs with meaningful content
                structured_paragraphs.append(paragraph)
        
        return '\n\n'.join(structured_paragraphs)

    def format_date(self, date_tuple):
        """Format date tuple to readable string."""
        try:
            if hasattr(date_tuple, 'strftime'):
                return date_tuple.strftime('%B %d, %Y')
            return str(date_tuple)
        except:
            return "Unknown date"

    def create_pdf(self, feed_url, max_articles=None):
        """Create a PDF from RSS feed articles."""
        try:
            articles = self.fetch_rss_feed(feed_url)
            
            if not articles:
                print("No articles found in the feed.")
                return
            
            if max_articles:
                articles = articles[:max_articles]
            
            print(f"Creating PDF with {len(articles)} articles...")
            
            # Create PDF with e-ink optimized settings
            doc = SimpleDocTemplate(
                self.output_file,
                pagesize=letter,
                rightMargin=72,  # 1 inch margins for e-ink
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            story = []
            
            # Title page for e-ink
            story.append(Paragraph("RSS Articles", self.title_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"Feed: {feed_url}", self.meta_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", self.meta_style))
            story.append(Paragraph(f"Articles: {len(articles)}", self.meta_style))
            story.append(PageBreak())
            
            # Process each article
            for i, article in enumerate(articles, 1):
                print(f"Processing article {i}/{len(articles)}: {article['title']}")
                
                # Article title
                story.append(Paragraph(article['title'], self.subtitle_style))
                story.append(Spacer(1, 8))
                
                # Article metadata
                if article.get('author'):
                    story.append(Paragraph(f"By: {article['author']}", self.meta_style))
                if article.get('published'):
                    story.append(Paragraph(f"Published: {article['published']}", self.meta_style))
                story.append(Paragraph(f"URL: {article['link']}", self.meta_style))
                story.append(Spacer(1, 12))
                
                # Extract and add article content
                content = self.extract_article_content(article['link'])
                if content:
                    self.add_formatted_content_to_story(content, story)
                else:
                    story.append(Paragraph("Content could not be extracted.", self.content_style))
                
                # Add page break between articles (except for the last one)
                if i < len(articles):
                    story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            print(f"PDF successfully created: {self.output_file}")
            
            # Get file size
            if os.path.exists(self.output_file):
                file_size = os.path.getsize(self.output_file) / 1024  # Convert to KB
                print(f"PDF created successfully: {self.output_file}")
                print(f"File size: {file_size:.1f} KB")
            else:
                print("Error: PDF file was not created")
            
        except Exception as e:
            print(f"Error creating PDF: {e}")
            raise

    def add_code_block_to_story(self, lines, story):
        """Add a code block to the story."""
        if not lines:
            return
        
        # Join the code lines
        code_text = '\n'.join(lines)
        
        # Create a special style for code blocks
        code_style = ParagraphStyle(
            'CustomCode',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            spaceBefore=12,
            textColor=black,
            alignment=TA_LEFT,
            leftIndent=20,
            rightIndent=20,
            fontName='Ubuntu' if self.ubuntu_fonts_available else 'Helvetica',
            leading=14,
            backColor=white,
            borderWidth=1,
            borderColor=black,
            borderPadding=8
        )
        
        try:
            story.append(Paragraph(f"<b>Code Block:</b><br/>{code_text}", code_style))
        except Exception as e:
            print(f"  Warning: Could not add code block: {e}")
    
    def add_image_to_story(self, image_url, alt_text, story):
        """Add an image to the story optimized for e-ink devices."""
        try:
            print(f"      Adding image to story: {alt_text} -> {image_url}")
            
            # Clean up the URL - handle Substack CDN URLs
            if 'substackcdn.com' in image_url:
                # Try to extract the base URL from the CDN URL
                # Pattern: https://substackcdn.com/image/fetch/.../https://...
                base_url_match = re.search(r'https://substackcdn\.com/image/fetch/[^/]+/(https://[^)]+)', image_url)
                if base_url_match:
                    image_url = base_url_match.group(1)
                    print(f"      Cleaned URL: {image_url}")
                else:
                    # Try alternative pattern for malformed URLs
                    base_url_match = re.search(r'https://substackcdn\.com/image/fetch/[^/]+/(https://[^)]+)', image_url.replace('$s!', '$s_!').replace('fauto', 'f_auto').replace('qauto', 'q_auto'))
                    if base_url_match:
                        image_url = base_url_match.group(1)
                        print(f"      Cleaned URL (alternative): {image_url}")
                    else:
                        # If we can't clean the URL, try to extract image ID and construct a working CDN URL
                        image_id_match = re.search(r'([a-f0-9-]+)_(\d+x\d+)\.(png|jpg|jpeg)', image_url)
                        if image_id_match:
                            image_id = image_id_match.group(1)
                            dimensions = image_id_match.group(2)
                            # Try to construct a working CDN URL using the image ID and original dimensions
                            image_url = f"https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https://substack-post-media.s3.amazonaws.com/public/images/{image_id}_{dimensions}.png"
                            print(f"      Constructed CDN URL from ID: {image_url}")
            
            # Add headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.oneusefulthing.org/'
            }
            
            # Download the image
            response = requests.get(image_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Open the image with PIL
            img_pil = PILImage.open(BytesIO(response.content))
            
            # Convert to grayscale for better e-ink display
            if img_pil.mode != 'L':
                img_pil = img_pil.convert('L')
            
            # Calculate image dimensions optimized for e-ink
            page_width = 400  # Smaller width for e-ink (was 500)
            img_width, img_height = img_pil.size
            
            # Scale image to fit page width while maintaining aspect ratio
            if img_width > page_width:
                scale_factor = page_width / img_width
                new_width = page_width
                new_height = int(img_height * scale_factor)
            else:
                new_width = img_width
                new_height = img_height
            
            # Ensure minimum height for readability on e-ink
            if new_height < 50:
                scale_factor = 50 / new_height
                new_width = int(new_width * scale_factor)
                new_height = 50
            
            # Convert PIL image to BytesIO for ReportLab
            img_bytes = BytesIO()
            img_pil.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Create a ReportLab Image object with proper sizing
            img_reportlab = Image(img_bytes, width=new_width, height=new_height)
            
            # Add the image to the story with e-ink optimized spacing
            story.append(Spacer(1, 16))  # Space before image
            story.append(img_reportlab)
            story.append(Spacer(1, 16))  # Space after image
            
            print(f"      Image added successfully (size: {new_width}x{new_height})")
            
        except Exception as e:
            print(f"      Warning: Could not add image: {e}")
            # Try alternative URL construction if the first attempt failed
            if 'substackcdn.com' in image_url and 's3.amazonaws.com' not in image_url:
                try:
                    # Extract image ID and try different CDN URL patterns
                    image_id_match = re.search(r'([a-f0-9-]+)_(\d+x\d+)\.(png|jpg|jpeg)', image_url)
                    if image_id_match:
                        image_id = image_id_match.group(1)
                        dimensions = image_id_match.group(2)
                        # Try different CDN URL patterns
                        alt_urls = [
                            f"https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https://substack-post-media.s3.amazonaws.com/public/images/{image_id}_{dimensions}.png",
                            f"https://substackcdn.com/image/fetch/w_520,h_272,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https://substack-post-media.s3.amazonaws.com/public/images/{image_id}_{dimensions}.png",
                            f"https://substackcdn.com/image/fetch/w_800,c_limit,f_auto,q_auto:good,fl_progressive:steep/https://substack-post-media.s3.amazonaws.com/public/images/{image_id}_{dimensions}.png"
                        ]
                        
                        for alt_url in alt_urls:
                            try:
                                print(f"      Trying alternative URL: {alt_url}")
                                response = requests.get(alt_url, headers=headers, timeout=15)
                                response.raise_for_status()
                                
                                img_pil = PILImage.open(BytesIO(response.content))
                                if img_pil.mode != 'L':
                                    img_pil = img_pil.convert('L')
                                
                                # Calculate dimensions
                                if img_pil.size[0] > 400:
                                    scale_factor = 400 / img_pil.size[0]
                                    new_width = 400
                                    new_height = int(img_pil.size[1] * scale_factor)
                                else:
                                    new_width, new_height = img_pil.size
                                
                                if new_height < 50:
                                    scale_factor = 50 / new_height
                                    new_width = int(new_width * scale_factor)
                                    new_height = 50
                                
                                img_bytes = BytesIO()
                                img_pil.save(img_bytes, format='PNG')
                                img_bytes.seek(0)
                                
                                img_reportlab = Image(img_bytes, width=new_width, height=new_height)
                                story.append(Spacer(1, 16))
                                story.append(img_reportlab)
                                story.append(Spacer(1, 16))
                                
                                print(f"      Image added successfully via alternative URL (size: {new_width}x{new_height})")
                                return
                                
                            except Exception as alt_e:
                                print(f"      Alternative URL failed: {alt_e}")
                                continue
                        
                except Exception as alt_e:
                    print(f"      All alternative URLs failed: {alt_e}")
            
            # Final fallback to text placeholder
            story.append(Paragraph(f"[Image: {alt_text if alt_text else 'Article image'} - Failed to load]", self.image_style))
    
    def add_formatted_content_to_story(self, content, story):
        """Add formatted content to the story."""
        lines = content.split('\n')
        current_code_block = []
        image_index = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Handle code blocks
            if line.startswith('CODE BLOCK:'):
                if current_code_block:
                    self.add_code_block_to_story(current_code_block, story)
                    current_code_block = []
                continue
            
            if current_code_block:
                current_code_block.append(line)
                continue
            
            # Handle headings
            if self.is_heading(line):
                self.add_heading_to_story(line, story)
                continue
            
            # Handle quotes
            if line.startswith('>'):
                self.add_quote_to_story(line, story)
                continue
            
            # Handle lists
            if self.is_list_item(line):
                self.add_list_item_to_story(line, story)
                continue
            
            # Handle images - use stored images from HTML
            if hasattr(self, 'current_article_images') and self.current_article_images and image_index < len(self.current_article_images):
                # Add images at regular intervals or when we detect image-related text
                if (image_index < len(self.current_article_images) and 
                    (any(img_alt.lower() in line.lower() for _, img_alt in self.current_article_images if img_alt) or
                     'image' in line.lower() or 'figure' in line.lower() or 'chart' in line.lower() or 'graph' in line.lower())):
                    
                    img_url, img_alt = self.current_article_images[image_index]
                    print(f"    Adding stored image {image_index + 1}: {img_alt} -> {img_url}")
                    self.add_image_to_story(img_url, img_alt, story)
                    image_index += 1
                    continue
            
            # Handle markdown image syntax as fallback
            if line.startswith('![') and '](' in line:
                print(f"    Found image line: {line}")
                # Extract alt text and URL from markdown image syntax
                match = re.match(r'!\[([^\]]*)\]\(([^)]*)\)', line)
                if match:
                    alt_text = match.group(1)
                    image_url = match.group(2)
                    print(f"    Processing image: {alt_text} -> {image_url}")
                    
                    # Try to fix corrupted URLs
                    if 'substackcdn.com' in image_url and '$s!' in image_url:
                        # Extract image ID from corrupted URL
                        image_id_match = re.search(r'([a-f0-9-]+)_(\d+x\d+)\.(png|jpg|jpeg)', image_url)
                        if image_id_match:
                            image_id = image_id_match.group(1)
                            dimensions = image_id_match.group(2)
                            # Construct a working CDN URL
                            image_url = f"https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https://substack-post-media.s3.amazonaws.com/public/images/{image_id}_{dimensions}.png"
                            print(f"    Fixed corrupted URL to: {image_url}")
                    
                    self.add_image_to_story(image_url, alt_text, story)
                else:
                    print(f"    Failed to parse image line: {line}")
                continue
            
            # Regular paragraph
            story.append(Paragraph(line, self.content_style))
            story.append(Spacer(1, 8))
        
        # Add any remaining code block
        if current_code_block:
            self.add_code_block_to_story(current_code_block, story)
        
        # Add any remaining images that weren't placed
        if hasattr(self, 'current_article_images') and self.current_article_images:
            for i in range(image_index, len(self.current_article_images)):
                img_url, img_alt = self.current_article_images[i]
                print(f"    Adding remaining image {i + 1}: {img_alt} -> {img_url}")
                self.add_image_to_story(img_url, img_alt, story)
    
    def is_heading(self, line):
        """Check if a line is a heading."""
        line = line.strip()
        
        # Check for markdown headings
        if re.match(r'^#{1,6}\s+', line):
            return True
        
        # Check for FAQ-style questions
        if re.match(r'^Q:\s*', line, re.IGNORECASE):
            return True
        
        # Check for all-caps section titles (common in academic writing)
        if line.isupper() and len(line) > 3 and len(line) < 100:
            return True
        
        # Check for common heading patterns
        heading_patterns = [
            r'^[A-Z][A-Za-z\s]+:$',  # Title followed by colon
            r'^[A-Z][A-Za-z\s]+\?$',  # Question format
            r'^[A-Z][A-Za-z\s]+\.$',  # Title followed by period
        ]
        
        for pattern in heading_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def is_list_item(self, line):
        """Check if line is a list item."""
        # Remove any escaped characters first
        clean_line = line.replace('\\', '')
        
        return (clean_line.startswith('- ') or 
                clean_line.startswith('* ') or 
                clean_line.startswith('• ') or
                re.match(r'^\d+\.', clean_line))
    
    def is_quote(self, line):
        """Check if line is a quote."""
        return line.startswith('> ') or line.startswith('"') or line.startswith('"')
    
    def add_heading_to_story(self, line, story):
        """Add a heading to the story."""
        # Remove markdown markers and determine heading level
        heading_level = 0
        clean_line = line.strip()
        
        # Count markdown heading levels
        if clean_line.startswith('#'):
            heading_level = len(clean_line) - len(clean_line.lstrip('#'))
            clean_line = re.sub(r'^#+\s*', '', clean_line)
        
        clean_line = clean_line.strip()
        
        if clean_line:
            try:
                # Choose style based on heading level
                if heading_level >= 3 or line.startswith('###'):
                    style = self.section_style
                elif heading_level >= 2 or line.startswith('##'):
                    style = self.subtitle_style
                else:
                    style = self.section_style
                
                story.append(Paragraph(clean_line, style))
                story.append(Spacer(1, 8))
            except Exception as e:
                print(f"  Warning: Could not add heading: {e}")
    
    def add_list_item_to_story(self, line, story):
        """Add a list item to the story."""
        # Clean up escaped characters first
        clean_line = line.replace('\\', '')
        
        # Remove list markers
        clean_line = re.sub(r'^[-*•]\s*', '', clean_line)
        clean_line = re.sub(r'^\d+\.\s*', '', clean_line)
        clean_line = clean_line.strip()
        
        if clean_line:
            try:
                story.append(Paragraph(f"• {clean_line}", self.list_style))
            except Exception as e:
                print(f"  Warning: Could not add list item: {e}")
    
    def add_quote_to_story(self, line, story):
        """Add a quote to the story."""
        # Remove quote markers
        clean_line = re.sub(r'^>\s*', '', line)
        clean_line = re.sub(r'^["\']\s*', '', line)
        clean_line = re.sub(r'\s*["\']$', '', line)
        clean_line = clean_line.strip()
        
        if clean_line:
            try:
                story.append(Paragraph(clean_line, self.quote_style))
                story.append(Spacer(1, 8))
            except Exception as e:
                print(f"  Warning: Could not add quote: {e}")
    
    def add_paragraph_to_story(self, text, story):
        """Add a paragraph to the story."""
        if not text.strip():
            return
        
        # Clean the text
        safe_text = re.sub(r'[^\x00-\x7F]+', '', text.strip())
        
        # Fix any remaining escaped characters
        safe_text = safe_text.replace('\\', '')
        
        if safe_text.strip():
            try:
                story.append(Paragraph(safe_text, self.content_style))
            except Exception as e:
                print(f"  Warning: Could not add paragraph: {e}")
                # Try with simpler text
                try:
                    simple_text = re.sub(r'[^\w\s\.\,\!\?\-\(\)]', '', safe_text)
                    if simple_text.strip():
                        story.append(Paragraph(simple_text, self.content_style))
                except:
                    pass

    def suggest_alternative_feeds(self, original_url):
        """Suggest alternative RSS feed URLs based on common patterns."""
        suggestions = []
        
        # Common RSS feed patterns
        common_patterns = [
            '/feed',
            '/rss',
            '/atom',
            '/feed.xml',
            '/rss.xml',
            '/atom.xml',
            '/feed/rss',
            '/feed/atom',
            '/blog/feed',
            '/news/feed',
            '/articles/feed',
            '/posts/feed'
        ]
        
        # Try to construct alternative URLs
        base_url = original_url.rstrip('/')
        
        # Remove common suffixes to get base URL
        for suffix in ['/feed', '/rss', '/atom', '/feed.xml', '/rss.xml', '/atom.xml']:
            if base_url.endswith(suffix):
                base_url = base_url[:-len(suffix)]
                break
        
        # Generate suggestions
        for pattern in common_patterns:
            suggestion = base_url + pattern
            if suggestion != original_url:
                suggestions.append(suggestion)
        
        # Add some common feed discovery URLs
        if 'blog' in original_url or 'news' in original_url:
            suggestions.extend([
                base_url + '/blog/feed',
                base_url + '/news/feed',
                base_url + '/articles/feed'
            ])
        
        return suggestions

    def check_feed_health(self, feed_url):
        """Check the health of an RSS feed and provide detailed feedback."""
        try:
            print(f"\n🏥 RSS Feed Health Check for: {feed_url}")
            print("=" * 60)
            
            # Validate the feed
            is_valid, validation_message = self.validate_rss_feed(feed_url)
            
            if not is_valid:
                print(f"\n❌ Feed validation failed!")
                print(f"   Error: {validation_message}")
                
                # Suggest alternatives
                suggestions = self.suggest_alternative_feeds(feed_url)
                if suggestions:
                    print(f"\n💡 Try these alternative RSS feed URLs:")
                    for i, suggestion in enumerate(suggestions[:5], 1):
                        print(f"   {i}. {suggestion}")
                
                return False
            
            # If valid, provide detailed health report
            feed = feedparser.parse(feed_url)
            
            print(f"\n📊 Feed Health Report:")
            print(f"   ✅ Status: Healthy")
            print(f"   📰 Title: {feed.feed.get('title', 'Unknown')}")
            print(f"   📝 Description: {feed.feed.get('description', 'No description')}")
            print(f"   🔗 Link: {feed.feed.get('link', 'No link')}")
            print(f"   📅 Last Updated: {feed.feed.get('updated', 'Unknown')}")
            print(f"   📄 Total Entries: {len(feed.entries)}")
            
            # Analyze entry quality
            if feed.entries:
                recent_entries = 0
                entries_with_content = 0
                
                for entry in feed.entries[:10]:
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        entry_date = datetime(*entry.published_parsed[:6])
                        if (datetime.now() - entry_date).days <= 30:
                            recent_entries += 1
                    
                    if getattr(entry, 'summary', None) or getattr(entry, 'content', None):
                        entries_with_content += 1
                
                print(f"   📅 Recent entries (30 days): {recent_entries}")
                print(f"   📝 Entries with content: {entries_with_content}")
                
                if recent_entries == 0:
                    print(f"   ⚠️  Warning: No recent entries found")
                if entries_with_content == 0:
                    print(f"   ⚠️  Warning: No entries with content found")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during health check: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Convert RSS feed to PDF')
    parser.add_argument('rss_url', help='URL of the RSS feed')
    parser.add_argument('-o', '--output', default='rss_articles.pdf', 
                       help='Output PDF filename (default: rss_articles.pdf)')
    parser.add_argument('-m', '--max-articles', type=int, 
                       help='Maximum number of articles to include (default: all)')
    parser.add_argument('--list-feeds', action='store_true',
                       help='List available feeds from the RSS URL')
    parser.add_argument('--health-check', action='store_true',
                       help='Perform detailed RSS feed health check')
    
    args = parser.parse_args()
    
    # Create converter
    converter = RSSToPDFConverter(args.output)
    
    # Health check if requested
    if args.health_check:
        success = converter.check_feed_health(args.rss_url)
        if not success:
            print(f"\n💡 Try running without --health-check to attempt PDF generation anyway.")
            sys.exit(1)
        return
    
    # Fetch RSS feed (includes automatic validation)
    print(f"\n🚀 Starting RSS to PDF conversion...")
    print(f"📡 Feed URL: {args.rss_url}")
    print(f"📄 Output file: {args.output}")
    if args.max_articles:
        print(f"📊 Max articles: {args.max_articles}")
    print("=" * 60)
    
    feed = converter.fetch_rss_feed(args.rss_url)
    
    if not feed:
        print(f"\n❌ Failed to fetch RSS feed.")
        print(f"💡 Try running with --health-check to diagnose the issue.")
        sys.exit(1)
    
    # List feeds if requested
    if args.list_feeds:
        print(f"\n📋 Feed Information:")
        print(f"Title: {feed.feed.get('title', 'Unknown')}")
        print(f"Description: {feed.feed.get('description', 'No description')}")
        print(f"Link: {feed.feed.get('link', 'No link')}")
        print(f"Number of articles: {len(feed.entries)}")
        print("\n📄 Articles:")
        for i, entry in enumerate(feed.entries[:10], 1):  # Show first 10
            print(f"{i}. {entry.get('title', 'Untitled')}")
        if len(feed.entries) > 10:
            print(f"... and {len(feed.entries) - 10} more articles")
        return
    
    # Create PDF
    print(f"\n📖 Creating PDF...")
    success = converter.create_pdf(args.rss_url, args.max_articles)
    
    if success:
        print(f"\n✅ PDF created successfully: {args.output}")
        print(f"📊 File size: {os.path.getsize(args.output) / 1024:.1f} KB")
        print(f"🎉 Ready for reading on your e-ink device!")
    else:
        print(f"\n❌ Failed to create PDF.")
        sys.exit(1)


if __name__ == "__main__":
    main() 