#!/usr/bin/env python
"""Quick test script"""
import sys
sys.path.insert(0, 'd:/mywork/url2md')

from url2md.converter import URL2MDConverter
from pathlib import Path
from datetime import datetime

def main():
    converter = URL2MDConverter()
    url = "https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus"
    
    print(f"Converting {url}...")
    try:
        # Prepare output path BEFORE conversion
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_测试.md"
        output_path = Path("d:/mywork/url2md/outputs") / filename
        
        # Convert with output path for logging
        markdown_content, page_title = converter.convert(url, str(output_path.absolute()))
        
        # Save to file
        output_path.write_text(markdown_content, encoding='utf-8')
        
        print(f"✓ Successfully converted to Markdown")
        print(f"✓ Saved to: {output_path}")
        print(f"✓ Lines: {len(markdown_content.splitlines())}")
        
        # Check if footer was removed
        lines = markdown_content.splitlines()
        has_footer = any('Less structure' in line or '产品' in line for line in lines[-20:])
        print(f"✓ Footer removed: {not has_footer}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
