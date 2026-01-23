# Translation Usage Examples

This document provides practical examples of using the translation feature in url2md.

## Quick Start

### 1. Basic Translation with Confirmation

```bash
# Convert webpage and translate (will ask for confirmation)
uv run url2md https://example.com/article --translate
```

This will:
1. Extract and convert the webpage to Markdown
2. Prompt you to confirm translation
3. Translate the content if you confirm

### 2. Auto-translate (No Confirmation)

```bash
# Convert and translate automatically using Ollama
uv run url2md https://example.com/article --auto-translate --provider ollama
```

## Provider-Specific Examples

### Using OpenAI

```bash
# With API key in command line
uv run url2md https://example.com/article \
  --auto-translate \
  --provider openai \
  --api-key sk-your-api-key \
  --model gpt-4o-mini

# With config file (recommended for API keys)
uv run url2md https://example.com/article \
  --auto-translate \
  --translation-config translation_config.json
```

**translation_config.json:**
```json
{
  "provider": "openai",
  "api_key": "sk-your-api-key",
  "model": "gpt-4o-mini",
  "target_language": "Chinese"
}
```

### Using Google Gemini

```bash
uv run url2md https://example.com/article \
  --auto-translate \
  --provider gemini \
  --api-key YOUR_GEMINI_KEY \
  --model gemini-2.0-flash-exp
```

### Using Ollama (Local)

```bash
# Make sure Ollama is running first
ollama serve

# In another terminal
uv run url2md https://example.com/article \
  --auto-translate \
  --provider ollama \
  --model llama3.2
```

**Advantages of Ollama:**
- No API costs
- Works offline
- Complete privacy
- Fast for local models

## Translating Different Languages

### To Chinese (Default)

```bash
uv run url2md https://example.com/article --auto-translate --provider ollama
```

### To Japanese

```bash
uv run url2md https://example.com/article \
  --auto-translate \
  --provider ollama \
  --target-language Japanese
```

### To Korean

```bash
uv run url2md https://example.com/article \
  --auto-translate \
  --provider ollama \
  --target-language Korean
```

## Programmatic Usage

### Simple Translation

```python
import asyncio
from pathlib import Path
from url2md.translator import TranslationConfig, translate_markdown_file

async def translate_my_file():
    # Configure
    config = TranslationConfig(
        provider="ollama",
        model="llama3.2",
        target_language="Chinese"
    )
    
    # Translate
    result = await translate_markdown_file(
        Path("outputs/article.md"),
        config,
        auto_translate=True
    )
    
    print(f"Translated: {result}")

# Run
asyncio.run(translate_my_file())
```

### With OpenAI

```python
import os
from url2md.translator import TranslationConfig

config = TranslationConfig(
    provider="openai",
    api_key=os.getenv("OPENAI_API_KEY"),  # From environment
    model="gpt-4o-mini",
    target_language="Chinese",
    temperature=0.3,
    chunk_size=3000
)
```

### With Custom Output Path

```python
result = await translate_markdown_file(
    input_path=Path("outputs/article.md"),
    output_path=Path("outputs/article_translated.md"),  # Custom path
    config=config,
    auto_translate=True
)
```

## Complete Workflow Example

```bash
# 1. Install dependencies
uv sync

# 2. Set up Ollama (if using local translation)
ollama pull llama3.2
ollama serve

# 3. Convert and translate in one command
uv run url2md https://python.org/about/ \
  --auto-translate \
  --provider ollama \
  --target-language Chinese \
  --verbose

# Output will show:
# ✓ Successfully converted to Markdown
# ✓ Saved to: outputs/20260119_120000_About_Python.md
# ============================================================
# Translation Workflow
# ============================================================
# [2026-01-19 12:00:01] Starting translation: outputs/20260119_120000_About_Python.md
# [2026-01-19 12:00:01] Loaded file: 1234 characters
# [2026-01-19 12:00:02] Translating chunk 1/1 (1234 chars)...
# [2026-01-19 12:00:05] ✓ Chunk 1/1 translated (1456 chars)
# [2026-01-19 12:00:05] ✓ Translation completed: outputs/20260119_120000_About_Python_zh.md
# ✓ Translation completed: outputs/20260119_120000_About_Python_zh.md
```

## Testing Translation

### Test with Sample File

```bash
# Run the quick test script
uv run python quick_test_translation.py
```

### Test Different Providers

```bash
# Test translation functionality
uv run python test_translation.py
```

## Troubleshooting

### Ollama Connection Error

**Error:** `httpx.ConnectError: All connection attempts failed`

**Solution:**
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, verify it's working
ollama list
```

### OpenAI API Error

**Error:** `401 Unauthorized`

**Solution:**
- Check your API key is correct
- Verify your API key has credits
- Make sure you're using the right API base URL

### Gemini API Error

**Error:** `403 Permission denied`

**Solution:**
- Enable Gemini API in Google Cloud Console
- Verify API key has correct permissions
- Check API quotas

## Advanced Configuration

### Large Documents (Chunking)

For very large documents, adjust chunk size:

```json
{
  "provider": "openai",
  "api_key": "sk-...",
  "chunk_size": 2000,
  "timeout": 300
}
```

### Quality vs Speed

```json
{
  "provider": "openai",
  "model": "gpt-4o",  // Higher quality, slower, more expensive
  "temperature": 0.1,  // More consistent translation
  "max_tokens": 8000
}
```

```json
{
  "provider": "openai",
  "model": "gpt-4o-mini",  // Faster, cheaper, still good quality
  "temperature": 0.3,
  "max_tokens": 4000
}
```

## Cost Comparison

| Provider | Model | Speed | Quality | Cost | Privacy |
|----------|-------|-------|---------|------|---------|
| OpenAI | gpt-4o-mini | Fast | Excellent | $0.15/1M tokens | API |
| OpenAI | gpt-4o | Medium | Best | $2.50/1M tokens | API |
| Gemini | gemini-2.0-flash | Very Fast | Excellent | Free tier available | API |
| Ollama | llama3.2 | Medium | Good | Free | Complete |

## Best Practices

1. **For production**: Use OpenAI or Gemini with proper error handling
2. **For development/testing**: Use Ollama to avoid API costs
3. **For privacy-sensitive content**: Use Ollama exclusively
4. **For best quality**: Use GPT-4o or Gemini Pro
5. **Store API keys**: Use config files or environment variables, never hardcode
6. **Monitor costs**: Check API usage regularly
7. **Test first**: Try with small documents before processing large batches

## Next Steps

- Read [TRANSLATION_CONFIG.md](TRANSLATION_CONFIG.md) for detailed configuration options
- Check [README.md](README.md) for complete project documentation
- Run `uv run url2md --help` to see all available options
