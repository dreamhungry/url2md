"""Command-line interface for URL to Markdown converter"""

import sys
import argparse
import re
import json
import asyncio
from pathlib import Path
from datetime import datetime
from .converter import URL2MDConverter
from .translator import TranslationConfig, translate_markdown_file


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


def _load_translation_config(args) -> TranslationConfig:
    """Load translation configuration from args or config file
    
    Args:
        args: Command line arguments
        
    Returns:
        TranslationConfig object
    """
    # If config file is provided, load from it
    if args.translation_config:
        config_path = Path(args.translation_config)
        if not config_path.exists():
            print(f"Warning: Config file not found: {config_path}", file=sys.stderr)
            print("Using command line arguments instead.")
        else:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
                return TranslationConfig(**config_dict)
            except Exception as e:
                print(f"Warning: Failed to load config file: {e}", file=sys.stderr)
                print("Using command line arguments instead.")
    
    # Build config from command line arguments
    config_kwargs = {
        'provider': args.provider,
        'target_language': args.target_language,
    }
    
    if args.api_key:
        config_kwargs['api_key'] = args.api_key
    
    if args.model:
        config_kwargs['model'] = args.model
    
    return TranslationConfig(**config_kwargs)





def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description='Convert web pages to Markdown format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  url2md https://example.com/article
  url2md https://blog.example.com/post --output custom_output
  url2md https://example.com/article --translate
  url2md https://example.com/article --auto-translate --provider ollama
  url2md https://example.com/article --translation-config config.json
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
    
    parser.add_argument(
        '-t', '--translate',
        action='store_true',
        help='Enable translation (will prompt for confirmation unless --auto-translate is set)'
    )
    
    parser.add_argument(
        '--auto-translate',
        action='store_true',
        help='Automatically translate without confirmation'
    )
    
    parser.add_argument(
        '--translation-config',
        type=str,
        help='Path to translation config JSON file'
    )
    
    parser.add_argument(
        '--target-language',
        type=str,
        default='Chinese',
        help='Target language for translation (default: Chinese)'
    )
    
    parser.add_argument(
        '--provider',
        type=str,
        choices=['openai', 'gemini', 'ollama'],
        default='openai',
        help='Translation API provider (default: openai)'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='API key for translation service'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        help='Model name for translation (e.g., gpt-4o-mini, gemini-2.0-flash-exp, llama3.2)'
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
        
        # Translation workflow
        if args.translate or args.auto_translate:
            print("\n" + "="*60)
            print("Translation Workflow")
            print("="*60)
            
            # Load translation config
            translation_config = _load_translation_config(args)
            
            # Translate the file
            try:
                translated_path = asyncio.run(
                    translate_markdown_file(
                        input_path=final_output_path,
                        config=translation_config,
                        auto_translate=args.auto_translate,
                    )
                )
                
                if translated_path:
                    print(f"✓ Translation completed: {translated_path.absolute()}")
                    
            except Exception as e:
                print(f"✗ Translation failed: {e}", file=sys.stderr)
                if args.verbose:
                    import traceback
                    traceback.print_exc()
                # Don't exit on translation failure, original file is still saved
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
