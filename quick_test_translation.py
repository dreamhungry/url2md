"""Quick test for translation workflow"""

import asyncio
from pathlib import Path
from url2md.translator import TranslationConfig, translate_markdown_file


async def main():
    """Quick test of translation functionality"""
    
    print("="*60)
    print("URL2MD Translation Quick Test")
    print("="*60)
    
    # Create a sample Markdown file
    sample_content = """# Getting Started with Python

Python is a high-level, interpreted programming language known for its simplicity and readability.

## Key Features

- **Easy to Learn**: Python has a simple syntax that's easy to understand
- **Versatile**: Used for web development, data science, AI, and more
- **Large Community**: Extensive libraries and community support

## Example Code

```python
def greet(name):
    return f"Hello, {name}!"

# Call the function
message = greet("World")
print(message)
```

## Resources

- [Official Documentation](https://docs.python.org)
- [Python Package Index](https://pypi.org)

## Conclusion

Python is an excellent choice for both beginners and experienced developers.
"""
    
    # Create test file
    test_file = Path("outputs/python_intro.md")
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text(sample_content, encoding='utf-8')
    
    print(f"\n✓ Created test file: {test_file}")
    print(f"  File size: {len(sample_content)} characters\n")
    
    # Test with Ollama (requires Ollama to be running locally)
    print("Testing translation with Ollama (local)...")
    print("-" * 60)
    print("NOTE: This requires Ollama to be installed and running.")
    print("If you don't have Ollama, you can:")
    print("1. Install it from: https://ollama.com")
    print("2. Run: ollama pull llama3.2")
    print("3. Run: ollama serve")
    print("-" * 60)
    
    config = TranslationConfig(
        provider="ollama",
        model="llama3.2",
        target_language="Chinese",
        temperature=0.3,
    )
    
    print(f"\nConfiguration:")
    print(f"  Provider: {config.provider}")
    print(f"  Model: {config.model}")
    print(f"  Target Language: {config.target_language}")
    print(f"  API Base: {config.api_base}")
    print()
    
    try:
        # Translate with user confirmation
        result = await translate_markdown_file(
            test_file,
            config,
            auto_translate=False  # Will prompt for confirmation
        )
        
        if result:
            print(f"\n{'='*60}")
            print("✓ Translation Successful!")
            print(f"{'='*60}")
            print(f"Original file: {test_file}")
            print(f"Translated file: {result}")
            print(f"Output size: {result.stat().st_size} bytes")
            
            # Show first few lines of translated content
            translated_content = result.read_text(encoding='utf-8')
            lines = translated_content.split('\n')
            print(f"\n{'='*60}")
            print("Preview of translated content (first 10 lines):")
            print(f"{'='*60}")
            for line in lines[:10]:
                print(line)
            if len(lines) > 10:
                print("...")
        else:
            print("\n✗ Translation was cancelled by user.")
    
    except Exception as e:
        print(f"\n{'='*60}")
        print("✗ Translation Failed")
        print(f"{'='*60}")
        print(f"Error: {e}")
        print("\nPossible solutions:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Make sure the model is available: ollama pull llama3.2")
        print("3. Or use a different provider (OpenAI/Gemini) with API key")
        print("\nExample with OpenAI:")
        print("  config = TranslationConfig(")
        print("      provider='openai',")
        print("      api_key='your-api-key',")
        print("      model='gpt-4o-mini'")
        print("  )")


if __name__ == "__main__":
    asyncio.run(main())
