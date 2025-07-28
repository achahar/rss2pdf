# Contributing to RSS to PDF Converter

Thank you for your interest in contributing to the RSS to PDF Converter! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

Before creating bug reports, please check the existing issues to avoid duplicates. When creating an issue, please include:

- **Clear and descriptive title**
- **Detailed description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **RSS feed URL** (if applicable)
- **System information** (OS, Python version)

### Feature Requests

We welcome feature requests! Please include:

- **Clear description** of the feature
- **Use case** explaining why this feature would be useful
- **Example implementation** (if possible)

### Code Contributions

#### Development Setup

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/RSS2PDF.git
   cd RSS2PDF
   ```
3. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

#### Coding Guidelines

- **Follow PEP 8** style guidelines
- **Add comments** for complex logic
- **Update documentation** for new features
- **Add tests** for new functionality
- **Keep commits atomic** and well-described

#### Testing

Before submitting a pull request:

1. **Run the test suite**:
   ```bash
   python test_installation.py
   ```
2. **Test with various RSS feeds**:
   ```bash
   python rss_to_pdf.py "https://news.ycombinator.com/rss" -m 2
   python rss_to_pdf.py "https://feeds.feedburner.com/TechCrunch/" -m 2
   ```
3. **Test error handling** with invalid URLs

#### Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following the coding guidelines
3. **Test thoroughly** with different RSS feeds
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

### Areas for Contribution

#### High Priority
- **RSS feed validation improvements**
- **Content extraction enhancements**
- **PDF formatting optimizations**
- **Error handling improvements**

#### Medium Priority
- **Additional output formats** (EPUB, HTML)
- **GUI interface**
- **Scheduling functionality**
- **Feed discovery features**

#### Low Priority
- **Mobile app**
- **Web interface**
- **Plugin system**

### Code Style

- **Python 3.7+** compatibility
- **Type hints** for function parameters
- **Docstrings** for all functions
- **Error handling** with specific exceptions
- **Logging** for debugging information

### Documentation

When adding new features, please update:

- **README.md** with usage examples
- **Inline comments** for complex logic
- **Function docstrings** with parameter descriptions

## Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code of Conduct**: Please be respectful and inclusive

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to RSS to PDF Converter! 🚀 