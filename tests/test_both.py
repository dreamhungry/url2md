import asyncio
from url2md.converter import URL2MDConverter
from pathlib import Path
from datetime import datetime

async def test_url(url, name):
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*80)
    
    converter = URL2MDConverter()
    
    try:
        # Prepare output path BEFORE conversion
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.md"
        output_path = Path("outputs") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        # Convert with output path for logging
        markdown_content, page_title = await converter.convert_async(url, str(output_path.absolute()))
        
        # Save to file
        output_path.write_text(markdown_content, encoding='utf-8')
        
        print(f"\n✓ Successfully converted to Markdown")
        print(f"✓ Saved to: {output_path.absolute()}")
        print(f"✓ Lines: {len(markdown_content.splitlines())}")
        
        # Check first 25 lines
        lines = markdown_content.splitlines()
        print(f"\n--- First 25 lines:")
        for i, line in enumerate(lines[:25]):
            preview = line[:90] if len(line) <= 90 else line[:87] + "..."
            print(f"{i+1:3d}: {preview}")
        
        return True
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    # Test 1: TigerData - should keep intro paragraph
    await test_url(
        "https://www.tigerdata.com/blog/pgvector-vs-qdrant",
        "TigerData"
    )
    
    await asyncio.sleep(2)
    
    # Test 2: DataCamp - should remove TOC
    await test_url(
        "https://www.datacamp.com/blog/the-top-5-vector-databases",
        "DataCamp"
    )

if __name__ == "__main__":
    asyncio.run(main())
