import asyncio
from url2md.converter import URL2MDConverter
from pathlib import Path
from datetime import datetime

async def test():
    converter = URL2MDConverter()
    url = "https://www.datacamp.com/blog/the-top-5-vector-databases"
    
    print(f"Testing: {url}")
    print("="*80)
    
    # Prepare output path BEFORE conversion
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_DataCamp_Sidebar_Test.md"
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
    
    # Check what should NOT be present (sidebar/navigation content)
    bad_content = {
        "Has 'GroupTraining more people' (sidebar)": any("GroupTraining more people" in line for line in lines),
        "Has 'Develop AI Applications' (sidebar)": any("Develop AI Applications" in line for line in lines[:30]),
        "Has 'Category' menu": any(line.strip() == "Category" for line in lines[:30]),
        "Has 'Technologies' menu": any(line.strip() == "Technologies" for line in lines[:30]),
        "Has 'Topics' menu": any(line.strip() == "Topics" for line in lines[:30]),
        "Has 'Browse Courses'": any("Browse Courses" in line for line in lines[:30]),
    }
    
    # Check what SHOULD be present (article content)
    good_content = {
        "Has article title": any("Vector Database" in line for line in lines[:10]),
        "Has 'What is a Vector Database?' section": any("What is a Vector Database?" in line for line in lines),
        "Has actual content paragraphs": len([l for l in lines if len(l.strip()) > 200]) > 5,
    }
    
    print(f"\n--- Content checks (should be TRUE):")
    for check, result in good_content.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check}: {result}")
    
    print(f"\n--- Sidebar checks (should be FALSE):")
    for check, result in bad_content.items():
        status = "✓" if not result else "✗"
        print(f"  {status} {check}: {result}")
    
    # Show first 30 lines
    print(f"\n--- First 30 lines:")
    for i, line in enumerate(lines[:30], start=1):
        preview = line[:90] if len(line) <= 90 else line[:87] + "..."
        print(f"{i:3d}: {preview}")
    
    # Summary
    all_good = all(good_content.values()) and not any(bad_content.values())
    print(f"\n{'='*80}")
    if all_good:
        print("✓✓✓ ALL CHECKS PASSED! Sidebar content correctly removed.")
    else:
        print("✗✗✗ SOME CHECKS FAILED! Please review the output.")
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(test())
