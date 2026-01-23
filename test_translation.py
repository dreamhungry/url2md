"""Test script for translation functionality"""

import asyncio
from pathlib import Path
from url2md.translator import TranslationConfig, translate_markdown_file


async def test_translation():
    """Test translation with different providers"""
    
    # Create a test Markdown file
    test_content = """# Test Document

This is a test document for translation.

## Features

- Markdown formatting preservation
- Code block handling
- Link preservation

## Code Example

```python
def hello():
    print("Hello, World!")
```

## Conclusion

This document tests the translation functionality.
"""
    
    test_file = Path("outputs/test_translation.md")
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text(test_content, encoding='utf-8')
    
    print("Test file created:", test_file)
    print("\n" + "="*60)
    
    # Test with Ollama (local, no API key needed)
    print("Testing with Ollama (local)...")
    print("="*60)
    
    config_ollama = TranslationConfig(
        provider="ollama",
        model="llama3.2",
        target_language="Chinese",
        temperature=0.3,
    )
    
    try:
        result = await translate_markdown_file(
            test_file,
            config_ollama,
            auto_translate=True  # Skip confirmation for testing
        )
        print(f"\n✓ Ollama translation successful: {result}")
    except Exception as e:
        print(f"\n✗ Ollama translation failed: {e}")
        print("Make sure Ollama is running: ollama serve")
    
    print("\n" + "="*60)
    print("\nTo test with OpenAI or Gemini:")
    print("1. Create translation_config.json with your API key")
    print("2. Run: python -m url2md.translator_test_with_config")


async def test_with_config_file():
    """Test translation with config file"""
    
    config_file = Path("translation_config.json")
    
    if not config_file.exists():
        print("Config file not found. Creating example...")
        example_config = {
            "provider": "openai",
            "api_key": "your-api-key-here",
            "model": "gpt-4o-mini",
            "target_language": "Chinese",
            "temperature": 0.3,
        }
        import json
        config_file.write_text(json.dumps(example_config, indent=2), encoding='utf-8')
        print(f"Created {config_file}")
        print("Please edit it with your API key and run again.")
        return
    
    # Load config
    import json
    with open(config_file, 'r', encoding='utf-8') as f:
        config_dict = json.load(f)
    
    config = TranslationConfig(**config_dict)
    
    # Find a test file
    test_file = Path("outputs/test_translation.md")
    if not test_file.exists():
        print("Creating test file...")
        test_content = "# Test\n\nThis is a test document."
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text(test_content, encoding='utf-8')
    
    # Translate
    result = await translate_markdown_file(
        test_file,
        config,
        auto_translate=True
    )
    
    print(f"\n✓ Translation successful: {result}")


if __name__ == "__main__":
    print("URL2MD Translation Test")
    print("="*60)
    print("\nThis will test the translation functionality.")
    print("Starting with Ollama (local) test...\n")
    
    asyncio.run(test_translation())
