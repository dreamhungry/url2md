# URL to Markdown Converter

An intelligent web-to-Markdown conversion tool powered by AI-driven content extraction that automatically filters navigation, ads, and footers, focusing on the main article content.

## Features

- 🌐 **Smart Content Extraction**: Advanced web scraping based on crawl4ai
- 🎯 **Precise Filtering**: Automatically identifies and removes navigation bars, sidebars, footers, and other irrelevant content
- 📊 **Link Density Analysis**: Accurately distinguishes content areas from navigation using link density algorithms
- 📝 **Perfect Format Preservation**: Maintains original heading hierarchy, lists, code blocks, and other formatting
- 📅 **Automatic File Management**: Timestamp-based naming with automatic output directory creation
- 🔍 **Detailed Logging**: All processing steps recorded to log files for debugging and optimization
- 🔧 **Managed by uv**: Fast and reliable Python package management

## Project Structure

```
url2md/
├── url2md/              # Core conversion module
│   ├── __init__.py      # Package initialization
│   ├── converter.py     # Main conversion logic
│   └── cli.py           # Command-line interface
├── tests/               # Test scripts
│   ├── test_datacamp.py          # DataCamp tests
│   ├── test_tigerdata.py         # TigerData tests
│   └── test_*.py                 # Other test files
├── outputs/             # Markdown output directory (auto-created)
├── log/                 # Debug log directory (auto-created)
├── pyproject.toml       # Project configuration and dependencies
├── uv.lock              # Dependency lock file
└── README.md            # Project documentation
```

## Technical Highlights

### 1. Smart Link Density Calculation

When calculating link density in regions, **link text length is excluded**, enabling accurate identification of navigation areas:

```python
# Incorrect calculation (diluted by link text)
link_density = link_count / total_text_length

# Correct calculation (accurately reflects link proportion)
link_density = link_count / (total_text_length - link_text_length)
```

### 2. Multi-Level Filtering Strategy

- **Header Detection**: Locates article start position via H1 title
- **Footer Detection**: Based on link density, H4 markers, and multiple patterns
- **Section Analysis**: Analyzes content characteristics section by section to distinguish body text from navigation
- **Cascade Detection**: Identifies consecutive high link-density regions

### 3. HTML + Markdown Dual Verification

Simultaneously analyzes HTML DOM structure and Markdown text features with cross-validation to improve accuracy.


## Installation

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager (required)

If you haven't installed uv yet, use the following commands:

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Project

```bash
# Clone or navigate to project directory
cd url2md

# Install dependencies using uv (recommended)
uv sync

# Or manual installation
uv venv
uv pip install -e .
```

## Usage

### Run Tests (Development Mode)

**⚠️ Important: Use the `uv run` command to run test scripts**

```bash
# Test DataCamp article conversion
uv run python tests/test_datacamp.py

# Test TigerData article conversion
uv run python tests/test_tigerdata.py

# Run other tests
uv run python tests/test_*.py
```

### View Logs

Each conversion run prints the log file path to the console:

```
📋 Log file: d:\mywork\url2md\log\clean_20260114_175230.log
📄 Output file: d:\mywork\url2md\outputs\20260114_175230_Article_Title.md
```

Log files contain detailed analysis processes:
- Character statistics for each section (excluding link text)
- Link count and density calculations
- Footer/Header identification decisions
- Content boundary determination process

### Basic Usage (Command Line)

```bash
# Convert webpage to Markdown
uv run url2md https://example.com/article

# Specify output directory
uv run url2md https://example.com/article --output my_docs

# Show verbose information
uv run url2md https://example.com/article --verbose
```

### Output Description

- **Markdown file directory**: `outputs/`
- **Log file directory**: `log/`
- **File naming format**: `YYYYMMDD_HHMMSS_Page_Title.md`
- **Example**: `20260114_143025_Python_Best_Practices.md`

## Examples

```bash
# Convert technical blog article
uv run python -c "from url2md.converter import URL2MDConverter; import asyncio; asyncio.run(URL2MDConverter().convert_async('https://example.com/article'))"

# Or use test scripts
uv run python tests/test_datacamp.py
```


## Output Format

Generated Markdown files contain:

1. **Article Title** (H1 level)
2. **Source URL** (Source link)
3. **Separator Line**
4. **Article Body Content**:
   - Preserves original heading hierarchy (H2, H3, H4...)
   - Preserves all links and images
   - Preserves code blocks and list formatting
   - Automatically removes navigation, sidebars, footers

## Core Dependencies

- **crawl4ai** - AI-driven web scraping and content extraction
- **beautifulsoup4** - HTML parsing and DOM analysis
- **html2text** - HTML to Markdown conversion
- **lxml** - Fast XML/HTML parser

## Development & Testing

### Run Tests

**⚠️ Always use `uv run` to run all test scripts:**

```bash
# Test DataCamp (articles with sidebars)
uv run python tests/test_datacamp.py

# Test TigerData (articles with footers)
uv run python tests/test_tigerdata.py

# Run full test suite
uv run python tests/test_both.py
```

### View Debug Logs

```bash
# Log files are saved in the log/ directory
# Filename format: clean_YYYYMMDD_HHMMSS.log

# View latest log (Windows PowerShell)
Get-Content -Tail 50 (Get-ChildItem log\*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1)

# View latest log (Linux/macOS)
tail -50 $(ls -t log/*.log | head -1)
```

### Understanding Log Output

Log files contain the following key information:

```
--- Section 0: What is a Vector Database?
    Lines: 25, Non-empty: 20, Link lines: 3
    Link count: 5, Text length (no links): 856
    Link ratio: 0.15, Links/100chars: 0.58
    Avg chars per link: 171.2
    >>> IS_FOOTER: False
```

- **Text length (no links)**: Pure content length after excluding link text
- **Link ratio**: Proportion of lines containing links
- **Links/100chars**: Number of links per 100 characters
- **IS_FOOTER**: Whether identified as footer/navigation area


## Algorithm Explanation

### Link Density Calculation

Key innovation: **Excluding link text when calculating link density**

```python
# Example: Navigation area
Raw text: "[Link1](url1) [Link2](url2) [Link3](url3)"
Traditional method: 3 links / 36 chars = 8.3%  ❌ Diluted
Improved method: 3 links / 0 chars = ∞      ✓ Accurate identification
```

### Footer Determination Rules

Identified as footer/navigation if any of the following conditions are met:

1. **Very high link density**: More than 3 links per 100 characters
2. **High proportion of link lines**: >70% of lines contain links, with total links >10
3. **Dense link list**: >12 links with average <80 characters per link
4. **Dual verification**: Both Markdown and HTML show high link density
5. **Excessive links**: Total link count >50 (typical footer characteristic)

### Header Identification Strategy

1. Find H1 title (article title) - most reliable marker
2. If no H1, use the first H2 title
3. Delete all content before the title (navigation, breadcrumbs, etc.)

## Notes

- Some websites have anti-scraping mechanisms that may require strategy adjustments
- JavaScript-rendered content relies on crawl4ai's rendering capabilities
- Please comply with target website's robots.txt and terms of use
- Large websites may require longer processing time (typically 10-30 seconds)

## Troubleshooting

### Issue: Navigation bar not filtered

**Solution**: Check link density calculations in log file
```bash
uv run python tests/test_datacamp.py
# Check Section analysis in log/clean_*.log
```

### Issue: Body content mistakenly deleted

**Cause**: Body text may contain many links (e.g., recommendation lists)
**Solution**: Adjust threshold parameters in `converter.py`

### Issue: Runtime errors

**Ensure using uv run**:
```bash
# ✓ Correct
uv run python tests/test_datacamp.py

# ✗ Incorrect (may lack dependencies)
python tests/test_datacamp.py
```

## Contributing

Issues and Pull Requests are welcome!

1. Fork this project
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add some AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Submit Pull Request

**When developing, please:**
- Use `uv run` to run all tests
- Review and analyze log files
- Add corresponding test cases

## License

MIT License - See LICENSE file for details

## Changelog

### v0.2.0 (2026-01-14)
- ✨ Fixed link density calculation (excluding link text length)
- 📋 Added detailed logging system
- 🎯 Improved Header/Footer identification algorithm
- 📝 Enhanced documentation and test instructions

### v0.1.0 (Initial release)
- Basic webpage to Markdown functionality
- Simple content filtering
