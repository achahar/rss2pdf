#!/usr/bin/env python3
"""
Test script to verify RSS to PDF converter installation and basic functionality.
"""

import sys
import importlib

def test_imports():
    """Test if all required modules can be imported."""
    required_modules = [
        'feedparser',
        'requests', 
        'bs4',
        'html2text',
        'reportlab',
        'PIL'
    ]
    
    print("Testing module imports...")
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing dependencies with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All modules imported successfully!")
        return True

def test_basic_functionality():
    """Test basic RSS to PDF functionality."""
    try:
        from rss_to_pdf import RSSToPDFConverter
        
        print("\nTesting basic functionality...")
        
        # Create converter
        converter = RSSToPDFConverter("test_output.pdf")
        
        # Test with a simple RSS feed
        test_url = "https://news.ycombinator.com/rss"
        print(f"Testing with: {test_url}")
        
        feed = converter.fetch_rss_feed(test_url)
        
        if feed and feed.entries:
            print(f"✅ Successfully fetched feed with {len(feed.entries)} articles")
            
            # Test PDF creation with just 1 article
            success = converter.create_pdf(feed, max_articles=1)
            
            if success:
                print("✅ Successfully created test PDF")
                import os
                if os.path.exists("test_output.pdf"):
                    size_kb = os.path.getsize("test_output.pdf") / 1024
                    print(f"✅ Test PDF created: {size_kb:.1f} KB")
                    # Clean up
                    os.remove("test_output.pdf")
                    print("✅ Test PDF cleaned up")
                else:
                    print("❌ Test PDF file not found")
                    return False
            else:
                print("❌ Failed to create test PDF")
                return False
        else:
            print("❌ Failed to fetch test RSS feed")
            return False
            
    except Exception as e:
        print(f"❌ Error during functionality test: {e}")
        return False
    
    return True

def main():
    print("RSS to PDF Converter - Installation Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test basic functionality
    if not test_basic_functionality():
        sys.exit(1)
    
    print("\n🎉 All tests passed! Your RSS to PDF converter is ready to use.")
    print("\nTry it out with:")
    print("python rss_to_pdf.py 'https://news.ycombinator.com/rss' -m 5")

if __name__ == "__main__":
    main() 