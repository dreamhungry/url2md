# Quick Fix for Translation Performance Issues

## 🚨 Problem: CPU at 100%, Translation Too Slow

## ✅ Solution: Use Faster Model

### Step 1: Install Fast Model
```bash
ollama pull llama3.2:3b
```

### Step 2: Create Config File
```bash
cat > translation_config.json << EOF
{
  "provider": "ollama",
  "model": "llama3.2:3b",
  "chunk_size": 1000,
  "timeout": 300
}
EOF
```

### Step 3: Translate
```bash
uv run url2md YOUR_URL --auto-translate --translation-config translation_config.json
```

## ⚡ Even Faster: Use Cloud API

```bash
uv run url2md YOUR_URL \
  --auto-translate \
  --provider openai \
  --api-key YOUR_OPENAI_KEY
```

## 🔍 Diagnose Issues

```bash
uv run python diagnose_translation.py
```

## 📖 More Info

- Performance Guide: `TRANSLATION_PERFORMANCE.md`
- All Fixes: `TRANSLATION_FIXES.md`
- Usage Examples: `TRANSLATION_USAGE.md`
