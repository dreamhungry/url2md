"""Command-line interface for URL to Markdown converter"""

import sys
import argparse
import re
from pathlib import Path
from datetime import datetime
from .converter import URL2MDConverter


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """Sanitize filename by removing invalid characters and replacing spaces
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Replace one or more consecutive spaces with a single underscore
    filename = re.sub(r'\s+', '_', filename)
    
    # Replace multiple consecutive underscores with a single underscore
    filename = re.sub(r'_+', '_', filename)
    
    # Limit length
    if len(filename) > max_length:
        filename = filename[:max_length]
    
    return filename.strip()


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description='Convert web pages to Markdown format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  url2md https://example.com/article
  url2md https://blog.example.com/post --output custom_output
        """
    )
    
    parser.add_argument(
        'url',
        help='URL of the web page to convert'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='outputs',
        help='Output directory (default: outputs)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate URL
    url = args.url.strip()
    if not url.startswith(('http://', 'https://')):
        print(f"Error: Invalid URL. Must start with http:// or https://", file=sys.stderr)
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.verbose:
        print(f"Fetching content from: {url}")
    
    try:
        # Create converter
        converter = URL2MDConverter()
        
        # Convert URL to Markdown (without output_path for now)
        markdown_content, page_title = converter.convert(url)
        
        # Generate final filename with actual page title
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title_part = sanitize_filename(page_title, max_length=50)
        final_filename = f"{timestamp}_{title_part}.md"
        final_output_path = output_dir / final_filename
        
        # Save to file with final name
        final_output_path.write_text(markdown_content, encoding='utf-8')
        
        # Now append the final path to the log file
        converter.log_final_output(str(final_output_path.absolute()))
        
        print(f"✓ Successfully converted to Markdown")
        print(f"✓ Saved to: {final_output_path.absolute()}")
        
        if args.verbose:
            print(f"\nPage title: {page_title}")
            print(f"Content length: {len(markdown_content)} characters")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
