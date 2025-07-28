# Quick Start Guide

Get your RSS to PDF converter running in minutes!

## Option 1: Automated Setup (Recommended)

1. **Run the setup script**:
   ```bash
   ./setup.sh
   ```

2. **Start using it**:
   ```bash
   source venv/bin/activate
   python rss_to_pdf.py "https://news.ycombinator.com/rss" -m 5
   ```

## Option 2: Manual Setup

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Test installation**:
   ```bash
   python test_installation.py
   ```

## Usage Examples

### Basic Usage
```bash
# Convert RSS feed to PDF
python rss_to_pdf.py "https://news.ycombinator.com/rss"

# Limit to 10 articles
python rss_to_pdf.py "https://news.ycombinator.com/rss" -m 10

# Specify output filename
python rss_to_pdf.py "https://news.ycombinator.com/rss" -o my_articles.pdf
```

### Popular RSS Feeds to Try

- **Hacker News**: `https://news.ycombinator.com/rss`
- **BBC News**: `http://feeds.bbci.co.uk/news/rss.xml`
- **TechCrunch**: `https://techcrunch.com/feed/`
- **Reddit Programming**: `https://www.reddit.com/r/programming/.rss`

### List Feed Information
```bash
python rss_to_pdf.py "https://news.ycombinator.com/rss" --list-feeds
```

## Troubleshooting

**"No module named 'cgi'"**: Update feedparser: `pip install --upgrade feedparser`

**Permission denied**: Make sure the script is executable: `chmod +x rss_to_pdf.py`

**Virtual environment not activated**: Always run `source venv/bin/activate` first

## What You Get

- ✅ Beautifully formatted PDF with proper typography
- ✅ Article titles, authors, and publication dates
- ✅ Full article content extraction
- ✅ Source links preserved
- ✅ Clean page breaks between articles
- ✅ Professional layout suitable for reading

Your PDF will be ready for offline reading on any device! 