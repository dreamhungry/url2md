import asyncio
from url2md.converter import URL2MDConverter
from pathlib import Path
from datetime import datetime

async def test():
    converter = URL2MDConverter()
    url = "https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus"
    
    print(f"Fetching {url}...")
    
    # Prepare output path BEFORE conversion
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Get page title first by fetching (we'll refetch during convert, but that's ok for testing)
    filename = f"{timestamp}_Manus_Test.md"
    output_path = Path("outputs") / filename
    output_path.parent.mkdir(exist_ok=True)
    
    # Convert with output path for logging
    markdown_content, page_title = await converter.convert_async(url, str(output_path.absolute()))
    
    # Save to file
    output_path.write_text(markdown_content, encoding='utf-8')
    
    print(f"✓ Successfully converted to Markdown")
    print(f"✓ Saved to: {output_path.absolute()}")
    print(f"✓ Content length: {len(markdown_content)} characters")

if __name__ == "__main__":
    asyncio.run(test())
