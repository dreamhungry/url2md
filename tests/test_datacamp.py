import asyncio
from url2md.converter import URL2MDConverter
from pathlib import Path
from datetime import datetime

async def test():
    converter = URL2MDConverter()
    url = "https://www.datacamp.com/blog/the-top-5-vector-databases"
    
    print(f"Fetching {url}...")
    
    # Prepare output path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_DataCamp_Test.md"
    output_path = Path("outputs") / filename
    output_path.parent.mkdir(exist_ok=True)
    
    # Convert with output path for logging
    markdown_content, page_title = await converter.convert_async(url, str(output_path.absolute()))
    
    # Save to file
    output_path.write_text(markdown_content, encoding='utf-8')
    
    print(f"✓ Saved to: {output_path.absolute()}")
    print(f"✓ Content length: {len(markdown_content)} characters")
    print(f"✓ Lines: {len(markdown_content.splitlines())}")
    
    # Check first 60 lines
    lines = markdown_content.splitlines()
    print("\n--- First 60 lines of output:")
    for i, line in enumerate(lines[:60]):
        print(f"{i+1:3d}: {line[:80]}")

if __name__ == "__main__":
    asyncio.run(test())
