#!/usr/bin/env python3
"""
Example usage of the RSS to PDF converter.
This script demonstrates how to use the RSSToPDFConverter class programmatically.
"""

from rss_to_pdf import RSSToPDFConverter

def main():
    # Example RSS feeds
    feeds = [
        {
            "name": "BBC News",
            "url": "http://feeds.bbci.co.uk/news/rss.xml",
            "output": "bbc_news.pdf",
            "max_articles": 10
        },
        {
            "name": "Hacker News",
            "url": "https://news.ycombinator.com/rss",
            "output": "hacker_news.pdf",
            "max_articles": 15
        }
    ]
    
    for feed_info in feeds:
        print(f"\n{'='*50}")
        print(f"Processing: {feed_info['name']}")
        print(f"URL: {feed_info['url']}")
        print(f"{'='*50}")
        
        # Create converter
        converter = RSSToPDFConverter(feed_info['output'])
        
        # Fetch RSS feed
        feed = converter.fetch_rss_feed(feed_info['url'])
        
        if feed:
            # List feed information
            print(f"Feed Title: {feed.feed.get('title', 'Unknown')}")
            print(f"Number of Articles: {len(feed.entries)}")
            
            # Create PDF
            success = converter.create_pdf(feed, feed_info['max_articles'])
            
            if success:
                print(f"✅ Successfully created: {feed_info['output']}")
            else:
                print(f"❌ Failed to create: {feed_info['output']}")
        else:
            print(f"❌ Failed to fetch feed: {feed_info['url']}")

if __name__ == "__main__":
    main() 