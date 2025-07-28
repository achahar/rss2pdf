# RSS to PDF Converter

A Python script that downloads articles from RSS feeds, formats them beautifully, and converts them to PDF for comfortable reading offline. **Perfect for e-ink devices!**

## ✨ Features

- **🔍 Automated RSS Validation** - Validates feeds before processing
- **📰 RSS Feed Parsing** - Supports standard RSS and Atom feeds
- **📄 Full Article Download** - Automatically fetches complete article content
- **🎨 Beautiful PDF Formatting** - Professional layout optimized for e-ink devices
- **📊 Metadata Preservation** - Includes author, publication date, and source links
- **🧠 Smart Content Extraction** - Intelligently extracts main content from web pages
- **⚙️ Customizable Output** - Control number of articles and output filename
- **🛡️ Robust Error Handling** - Graceful handling of network issues and malformed feeds
- **🏥 Health Check System** - Detailed RSS feed analysis and troubleshooting

## 🚀 Quick Start

### Installation

1. **Clone or download the files**:
   ```bash
   git clone <repository-url>
   cd RSS2PDF
   ```

2. **Run the setup script** (recommended):
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   **Or install manually**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 📖 Usage

### Basic Usage

Convert an RSS feed to PDF:
```bash
python rss_to_pdf.py "https://example.com/feed.xml"
```

### Advanced Usage

**Specify output filename**:
```bash
python rss_to_pdf.py "https://example.com/feed.xml" -o my_articles.pdf
```

**Limit number of articles**:
```bash
python rss_to_pdf.py "https://example.com/feed.xml" -m 10
```

**Health check RSS feed**:
```bash
python rss_to_pdf.py "https://example.com/feed.xml" --health-check
```

**List feed information**:
```bash
python rss_to_pdf.py "https://example.com/feed.xml" --list-feeds
```

**Combine options**:
```bash
python rss_to_pdf.py "https://example.com/feed.xml" -o tech_news.pdf -m 20
```

## 📰 Popular RSS Feed Examples

### Tech & News
```bash
# Hacker News
python rss_to_pdf.py "https://news.ycombinator.com/rss" -o hacker_news.pdf

# TechCrunch
python rss_to_pdf.py "https://feeds.feedburner.com/TechCrunch/" -o techcrunch.pdf

# BBC News
python rss_to_pdf.py "http://feeds.bbci.co.uk/news/rss.xml" -o bbc_news.pdf

# OpenAI News
python rss_to_pdf.py "https://openai.com/news/rss.xml" -o openai_news.pdf
```

### Blogs & Publications
```bash
# One Useful Thing (Substack)
python rss_to_pdf.py "https://www.oneusefulthing.org/feed" -o one_useful_thing.pdf

# Simon Willison's Blog
python rss_to_pdf.py "https://simonwillison.net/atom/everything/" -o simon_willison.pdf
```

## 🏥 RSS Feed Health Check

The new health check feature automatically validates RSS feeds and provides detailed feedback:

```bash
python rss_to_pdf.py "https://example.com/feed.xml" --health-check
```

**What it checks**:
- ✅ **Network connectivity** - Ensures the feed URL is accessible
- ✅ **Content type validation** - Verifies it's actually RSS/XML
- ✅ **Feed structure** - Checks for proper RSS/Atom format
- ✅ **Entry validation** - Ensures entries have required fields
- ✅ **Content freshness** - Identifies feeds with recent updates
- ✅ **Alternative suggestions** - Suggests other RSS URLs if needed

## 📋 Command Line Options

| Option | Description |
|--------|-------------|
| `rss_url` | URL of the RSS feed (required) |
| `-o, --output` | Output PDF filename (default: rss_articles.pdf) |
| `-m, --max-articles` | Maximum number of articles to include |
| `--list-feeds` | List feed information without creating PDF |
| `--health-check` | Perform detailed RSS feed health check |

## 🎨 PDF Features

### E-ink Optimization
- **High contrast** black text on white background
- **Clean Ubuntu fonts** for maximum readability
- **Justified text** for professional appearance
- **Proper margins** (1-inch) for comfortable reading
- **Grayscale images** optimized for e-ink displays

### Content Structure
- **Title page** with feed information
- **Article headers** with clear titles and metadata
- **Content layout** with proper spacing and typography
- **Source links** preserved for reference
- **Page breaks** for clean article separation

## 🧠 Smart Content Extraction

The script intelligently extracts content using multiple strategies:

1. **RSS feed content** - Uses full content if available in the feed
2. **Article URLs** - Downloads complete articles from source websites
3. **Content selectors** - Uses multiple CSS selectors to find main content
4. **HTML cleaning** - Removes ads, navigation, and other non-content elements
5. **Image handling** - Includes relevant images with proper sizing

## 🛡️ Error Handling

- **Network timeout protection** - Handles slow or unresponsive servers
- **Malformed RSS handling** - Graceful parsing of non-standard feeds
- **Content extraction fallbacks** - Multiple strategies for different websites
- **User-friendly error messages** - Clear feedback about what went wrong
- **Alternative suggestions** - Helps find correct RSS URLs when validation fails

## 📦 Dependencies

- `feedparser>=6.0.10` - RSS/Atom feed parsing
- `requests==2.31.0` - HTTP requests for article downloading
- `beautifulsoup4==4.12.2` - HTML parsing and content extraction
- `reportlab==4.0.4` - PDF generation
- `Pillow>=10.0.0` - Image processing
- `html2text==2020.1.16` - HTML to text conversion

## 🔧 Troubleshooting

### Common Issues

**"No articles found in RSS feed"**
- Check if the RSS URL is correct
- Verify the feed is publicly accessible
- Try the `--health-check` option to diagnose issues

**"Error fetching RSS feed"**
- Check your internet connection
- Verify the RSS URL is valid
- Some feeds may require authentication

**"Error creating PDF"**
- Ensure you have write permissions in the current directory
- Check if the output filename is valid
- Verify all dependencies are installed

**Large PDF files**
- Use the `-m` option to limit articles
- Some feeds contain large images or content

### Performance Tips

- Use `-m` to limit articles for faster processing
- The script includes delays between requests to be respectful to servers
- For large feeds, consider processing in batches

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Ubuntu Font Family** - For beautiful typography
- **Feedparser** - For robust RSS parsing
- **ReportLab** - For professional PDF generation
- **BeautifulSoup** - For intelligent content extraction

---

**Perfect for reading on Kindle, Kobo, and other e-ink devices! 📚✨** 