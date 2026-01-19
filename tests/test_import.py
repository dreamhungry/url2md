#!/usr/bin/env python
import sys
import traceback

try:
    print("Importing URL2MDConverter...")
    from url2md.converter import URL2MDConverter
    print("✓ Import successful")
    
    print("\nCreating instance...")
    converter = URL2MDConverter()
    print("✓ Instance created")
    
    print("\nTesting _calculate_text_length_without_links...")
    text = "This is [a link](http://example.com) and [another](http://test.com)."
    length, count = converter._calculate_text_length_without_links(text)
    print(f"  Text: {text}")
    print(f"  Length without links: {length}")
    print(f"  Link count: {count}")
    print("✓ Function works")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    traceback.print_exc()
    sys.exit(1)
