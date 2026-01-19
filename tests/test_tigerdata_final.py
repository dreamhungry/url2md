import asyncio
from url2md.converter import URL2MDConverter
from pathlib import Path
from datetime import datetime

async def test():
    converter = URL2MDConverter()
    url = "https://www.tigerdata.com/blog/pgvector-vs-qdrant"
    
    print(f"Testing: {url}")
    print("="*80)
    
    # Prepare output path BEFORE conversion
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_TigerData_Final.md"
    output_path = Path("outputs") / filename
    output_path.parent.mkdir(exist_ok=True)
    
    # Convert with output path for logging
    markdown_content, page_title = await converter.convert_async(url, str(output_path.absolute()))
    
    # Save to file
    output_path.write_text(markdown_content, encoding='utf-8')
    
    print(f"\n✓ Successfully converted to Markdown")
    print(f"✓ Saved to: {output_path.absolute()}")
    
    lines = markdown_content.splitlines()
    print(f"✓ Total lines: {len(lines)}")
    
    # Check critical content
    has_intro = any("Can you stick with PostgreSQL" in line for line in lines[:30])
    has_when_to_choose = any("When to choose each solution" in line for line in lines)
    has_get_started = any("Get started today" in line for line in lines)
    has_community = any("Get involved with the pgvectorscale community" in line for line in lines)
    
    print(f"\n--- Content checks:")
    print(f"  ✓ Has intro paragraph: {has_intro}")
    print(f"  ✓ Has 'When to choose' section: {has_when_to_choose}")
    print(f"  ✓ Has 'Get started today': {has_get_started}")
    print(f"  ✓ Has community section: {has_community}")
    
    # Show last 15 lines
    print(f"\n--- Last 15 lines:")
    for i, line in enumerate(lines[-15:], start=len(lines)-14):
        preview = line[:100] if len(line) <= 100 else line[:97] + "..."
        print(f"{i:3d}: {preview}")
    
    # Count specific sections
    when_to_choose_line = None
    for i, line in enumerate(lines):
        if "When to choose each solution" in line:
            when_to_choose_line = i
            break
    
    if when_to_choose_line:
        print(f"\n✓ 'When to choose' found at line {when_to_choose_line + 1}")
        print(f"  Content after this:")
        for i in range(when_to_choose_line, min(when_to_choose_line + 20, len(lines))):
            preview = lines[i][:90] if len(lines[i]) <= 90 else lines[i][:87] + "..."
            print(f"  {i+1:3d}: {preview}")
    else:
        print(f"\n✗ 'When to choose' section NOT FOUND - content was incorrectly removed!")

if __name__ == "__main__":
    asyncio.run(test())
