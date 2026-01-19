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
    filename = f"{timestamp}_TigerData_Complete.md"
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
    
    # Check critical content presence
    checks = {
        "Has intro paragraph": any("Can you stick with PostgreSQL" in line for line in lines[:30]),
        "Has 'When to choose' section": any("When to choose each solution" in line for line in lines),
        "Has 'Get started today'": any("Get started today" in line for line in lines),
        "Has 'Get involved' section": any("Get involved with the pgvectorscale community" in line for line in lines),
    }
    
    # Check what should NOT be present (footer content)
    bad_content = {
        "Has 'Related posts' (SHOULD BE REMOVED)": any("Related posts" in line for line in lines),
        "Has 'Stay updated' (SHOULD BE REMOVED)": any("Stay updated with new posts" in line for line in lines),
        "Has 'Products' nav (SHOULD BE REMOVED)": any(line.strip() == "Products" for line in lines),
        "Has 'Learn' nav (SHOULD BE REMOVED)": any(line.strip() == "Learn" for line in lines),
        "Has 'Company' nav (SHOULD BE REMOVED)": any(line.strip() == "Company" for line in lines),
    }
    
    print(f"\n--- Content checks (should be TRUE):")
    for check, result in checks.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check}: {result}")
    
    print(f"\n--- Footer checks (should be FALSE):")
    for check, result in bad_content.items():
        status = "✓" if not result else "✗"
        print(f"  {status} {check}: {result}")
    
    # Show last 15 lines
    print(f"\n--- Last 15 lines:")
    for i, line in enumerate(lines[-15:], start=len(lines)-14):
        preview = line[:100] if len(line) <= 100 else line[:97] + "..."
        print(f"{i:3d}: {preview}")
    
    # Summary
    all_good = all(checks.values()) and not any(bad_content.values())
    print(f"\n{'='*80}")
    if all_good:
        print("✓✓✓ ALL CHECKS PASSED! Content is correctly filtered.")
    else:
        print("✗✗✗ SOME CHECKS FAILED! Please review the output.")
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(test())
