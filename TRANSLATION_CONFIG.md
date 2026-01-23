# Translation Configuration Examples

This file shows how to configure the translation agent for different providers.

## Configuration File Format (JSON)

Create a `translation_config.json` file:

```json
{
  "provider": "openai",
  "api_key": "your-api-key-here",
  "model": "gpt-4o-mini",
  "target_language": "Chinese",
  "temperature": 0.3,
  "chunk_size": 3000
}
```

## Provider-Specific Examples

### 1. OpenAI API

```json
{
  "provider": "openai",
  "api_key": "sk-...",
  "api_base": "https://api.openai.com/v1",
  "model": "gpt-4o-mini",
  "target_language": "Chinese",
  "temperature": 0.3,
  "max_tokens": 4000,
  "chunk_size": 3000,
  "timeout": 120
}
```

Available models: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo`

### 2. Google Gemini API

```json
{
  "provider": "gemini",
  "api_key": "AIza...",
  "api_base": "https://generativelanguage.googleapis.com/v1beta",
  "model": "gemini-2.0-flash-exp",
  "target_language": "Chinese",
  "temperature": 0.3,
  "max_tokens": 4000,
  "chunk_size": 3000,
  "timeout": 120
}
```

Available models: `gemini-2.0-flash-exp`, `gemini-1.5-pro`, `gemini-1.5-flash`

### 3. Ollama (Local)

```json
{
  "provider": "ollama",
  "api_base": "http://localhost:11434/v1",
  "model": "llama3.2",
  "target_language": "Chinese",
  "temperature": 0.3,
  "chunk_size": 2000,
  "timeout": 300
}
```

**Note**: No API key needed for Ollama. Make sure Ollama is running locally.

Available models: `llama3.2`, `llama3.1`, `qwen2.5`, `gemma2`, etc.

### 4. OpenAI-Compatible APIs (e.g., DeepSeek, local vLLM)

```json
{
  "provider": "openai",
  "api_key": "your-api-key",
  "api_base": "https://api.deepseek.com/v1",
  "model": "deepseek-chat",
  "target_language": "Chinese",
  "temperature": 0.3,
  "chunk_size": 3000,
  "timeout": 120
}
```

## Language Options

Supported target languages:
- `"Chinese"` or `"中文"` or `"简体中文"` → zh
- `"English"` → en
- `"Japanese"` or `"日语"` → ja
- `"Korean"` or `"韩语"` → ko
- `"French"` → fr
- `"German"` → de
- `"Spanish"` → es

## Configuration Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `provider` | string | Yes | `"openai"` | API provider: `"openai"`, `"gemini"`, or `"ollama"` |
| `api_key` | string | Conditional | None | API key (required for OpenAI/Gemini, not for Ollama) |
| `api_base` | string | No | Auto | Base URL for API endpoint |
| `model` | string | No | Auto | Model name to use |
| `target_language` | string | No | `"Chinese"` | Target language for translation |
| `temperature` | float | No | `0.3` | Sampling temperature (0.0-1.0) |
| `max_tokens` | int | No | None | Maximum tokens in response |
| `chunk_size` | int | No | `3000` | Characters per chunk for large documents |
| `timeout` | int | No | `120` | Request timeout in seconds |

## Usage in Code

### Basic Usage

```python
import asyncio
from pathlib import Path
from url2md.translator import TranslationConfig, translate_markdown_file

# Create config
config = TranslationConfig(
    provider="openai",
    api_key="your-api-key",
    model="gpt-4o-mini",
    target_language="Chinese"
)

# Translate file
input_file = Path("outputs/article.md")
result = asyncio.run(translate_markdown_file(input_file, config))
print(f"Translated file: {result}")
```

### Load Config from JSON

```python
import json
from pathlib import Path
from url2md.translator import TranslationConfig

# Load config from file
with open("translation_config.json") as f:
    config_dict = json.load(f)

config = TranslationConfig(**config_dict)
```

### With User Confirmation

```python
# Will prompt user to confirm before translating
result = asyncio.run(
    translate_markdown_file(
        input_file,
        config,
        auto_translate=False  # Prompt for confirmation
    )
)
```

### Auto-translate (No Confirmation)

```python
# Skip confirmation prompt
result = asyncio.run(
    translate_markdown_file(
        input_file,
        config,
        auto_translate=True  # No prompt
    )
)
```

## Environment Variables

You can also use environment variables for API keys:

```bash
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="AIza..."
```

Then in code:

```python
import os

config = TranslationConfig(
    provider="openai",
    api_key=os.getenv("OPENAI_API_KEY"),
    target_language="Chinese"
)
```

## Tips

1. **Chunk Size**: Adjust based on model's context window and API costs
   - Larger chunks = fewer API calls but higher token usage
   - Smaller chunks = more API calls but better error recovery

2. **Temperature**: Lower values (0.1-0.3) for more consistent translations

3. **Timeout**: Increase for slower models or large documents

4. **Ollama**: Best for privacy and offline use, but may be slower

5. **Model Selection**:
   - For quality: `gpt-4o`, `gemini-1.5-pro`
   - For speed/cost: `gpt-4o-mini`, `gemini-2.0-flash-exp`
   - For local: `llama3.2`, `qwen2.5`
