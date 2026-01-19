import asyncio
from url2md.converter import URL2MDConverter
from pathlib import Path
from datetime import datetime

async def test_url(url, name, checks):
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
        
        lines = markdown_content.splitlines()
        print(f"✓ Total lines: {len(lines)}")
        
        # Run checks
        good_checks = checks['should_have']
        bad_checks = checks['should_not_have']
        
        good_results = {}
        for desc, test_func in good_checks.items():
            good_results[desc] = test_func(lines)
        
        bad_results = {}
        for desc, test_func in bad_checks.items():
            bad_results[desc] = test_func(lines)
        
        print(f"\n--- Content checks (should be TRUE):")
        for desc, result in good_results.items():
            status = "✓" if result else "✗"
            print(f"  {status} {desc}: {result}")
        
        print(f"\n--- Unwanted content checks (should be FALSE):")
        for desc, result in bad_results.items():
            status = "✓" if not result else "✗"
            print(f"  {status} {desc}: {result}")
        
        # Show first and last lines
        print(f"\n--- First 15 lines:")
        for i, line in enumerate(lines[:15], start=1):
            preview = line[:90] if len(line) <= 90 else line[:87] + "..."
            print(f"{i:3d}: {preview}")
        
        print(f"\n--- Last 10 lines:")
        for i, line in enumerate(lines[-10:], start=len(lines)-9):
            preview = line[:90] if len(line) <= 90 else line[:87] + "..."
            print(f"{i:3d}: {preview}")
        
        # Summary
        all_good = all(good_results.values()) and not any(bad_results.values())
        print(f"\n{'='*80}")
        if all_good:
            print(f"✓✓✓ {name}: ALL CHECKS PASSED!")
        else:
            print(f"✗✗✗ {name}: SOME CHECKS FAILED!")
        print(f"{'='*80}")
        
        return all_good
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    # Test 1: DataCamp - should remove sidebar and footer
    datacamp_checks = {
        'should_have': {
            'Has article title': lambda lines: any("Vector Database" in line for line in lines[:10]),
            'Has "What is a Vector Database?"': lambda lines: any("What is a Vector Database?" in line for line in lines),
            'Has substantial content': lambda lines: len([l for l in lines if len(l.strip()) > 200]) > 5,
        },
        'should_not_have': {
            'Has "GroupTraining" sidebar': lambda lines: any("GroupTraining more people" in line for line in lines),
            'Has "Develop AI Applications" sidebar': lambda lines: any("Develop AI Applications" in line for line in lines[:30]),
            'Has TOC "Contents"': lambda lines: any(line.strip() == "Contents" for line in lines[:30]),
            'Has "Category" menu': lambda lines: any(line.strip() == "Category" for line in lines[:30]),
            'Has "Grow your data skills" footer': lambda lines: any("Grow your data skills with DataCamp" in line for line in lines),
        }
    }
    
    result1 = await test_url(
        "https://www.datacamp.com/blog/the-top-5-vector-databases",
        "DataCamp_Final",
        datacamp_checks
    )
    
    await asyncio.sleep(2)
    
    # Test 2: TigerData - should remove header nav and footer
    tigerdata_checks = {
        'should_have': {
            'Has intro paragraph': lambda lines: any("Can you stick with PostgreSQL" in line for line in lines),
            'Has "When to choose"': lambda lines: any("When to choose each solution" in line for line in lines),
            'Has "Get started today"': lambda lines: any("Get started today" in line for line in lines),
        },
        'should_not_have': {
            'Has "Related posts" footer': lambda lines: any("Related posts" in line for line in lines),
            'Has "Stay updated" footer': lambda lines: any("Stay updated with new posts" in line for line in lines),
            'Has "Products" navigation': lambda lines: any(line.strip() == "Products" for line in lines),
        }
    }
    
    result2 = await test_url(
        "https://www.tigerdata.com/blog/pgvector-vs-qdrant",
        "TigerData_Final",
        tigerdata_checks
    )
    
    # Final summary
    print(f"\n\n{'#'*80}")
    print("FINAL SUMMARY")
    print(f"{'#'*80}")
    print(f"DataCamp test: {'✓ PASSED' if result1 else '✗ FAILED'}")
    print(f"TigerData test: {'✓ PASSED' if result2 else '✗ FAILED'}")
    if result1 and result2:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print("\n⚠️  Some tests failed. Please review the output.")
    print(f"{'#'*80}")

if __name__ == "__main__":
    asyncio.run(main())
