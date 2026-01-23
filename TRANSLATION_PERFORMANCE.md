# Translation Performance Optimization Guide

## Common Performance Issues

### Issue 1: High CPU Usage (100%)

**Symptoms:**
- CPU usage spikes to 100%
- System becomes unresponsive
- Translation takes very long time

**Causes:**
- Ollama model is computing on CPU instead of GPU
- Model is too large for available hardware
- Chunk size is too large

**Solutions:**

#### 1. Use GPU Acceleration (Recommended)

Check if Ollama is using GPU:
```bash
ollama ps
```

If not using GPU, reinstall Ollama with CUDA support (NVIDIA) or ensure Metal/ROCm is enabled (AMD).

#### 2. Use Smaller Models

Replace large models with smaller, faster ones:

```json
{
  "model": "qwen2.5:7b"  // Instead of qwen3:8b or larger
}
```

Recommended models for speed:
- `llama3.2:3b` - Fast, good quality
- `qwen2.5:7b` - Balanced
- `gemma2:2b` - Very fast, lower quality

#### 3. Reduce Chunk Size

Smaller chunks = less computation per request:

```json
{
  "chunk_size": 1000  // Down from 2000 or 3000
}
```

Trade-off: More chunks = more API calls but faster per-chunk processing.

#### 4. Increase Timeout

Prevent premature timeouts:

```json
{
  "timeout": 600  // 10 minutes instead of 300s (5 minutes)
}
```

### Issue 2: Timeout Errors

**Error:**
```
Translation request timed out after 300s
```

**Solutions:**

1. **Increase timeout**:
```json
{
  "timeout": 600
}
```

2. **Reduce chunk size**:
```json
{
  "chunk_size": 1000
}
```

3. **Use faster model**:
```json
{
  "model": "llama3.2:3b"
}
```

### Issue 3: Memory Issues

**Symptoms:**
- System runs out of memory
- Ollama crashes
- Translation fails midway

**Solutions:**

1. **Use smaller models**:
   - 3B parameter models use ~2GB RAM
   - 7B parameter models use ~4-5GB RAM
   - 8B+ parameter models use ~6-8GB RAM

2. **Close other applications**

3. **Set max_tokens limit**:
```json
{
  "max_tokens": 2000
}
```

## Optimal Configurations

### For Speed (Fast Translation)

**Best for:** Quick translations, testing

```json
{
  "provider": "ollama",
  "model": "llama3.2:3b",
  "chunk_size": 1000,
  "timeout": 300,
  "temperature": 0.3
}
```

### For Quality (Best Results)

**Best for:** Production, important documents

```json
{
  "provider": "openai",
  "api_key": "your-key",
  "model": "gpt-4o-mini",
  "chunk_size": 3000,
  "timeout": 120,
  "temperature": 0.3
}
```

### For Privacy (Offline)

**Best for:** Sensitive content

```json
{
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "chunk_size": 1500,
  "timeout": 600,
  "temperature": 0.3
}
```

### For Large Documents

**Best for:** Long articles, books

```json
{
  "provider": "openai",
  "api_key": "your-key",
  "model": "gpt-4o-mini",
  "chunk_size": 2000,
  "timeout": 180,
  "max_tokens": 4000
}
```

## Model Comparison

| Model | Speed | Quality | RAM Usage | CPU Impact |
|-------|-------|---------|-----------|------------|
| `llama3.2:3b` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 2GB | Low |
| `qwen2.5:7b` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 4-5GB | Medium |
| `qwen3:8b` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 6-8GB | High |
| `llama3.1:8b` | ⭐⭐⭐ | ⭐⭐⭐⭐ | 6-8GB | High |
| `gpt-4o-mini` (API) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | N/A | None |

## Hardware Recommendations

### Minimum (CPU Only)
- **CPU:** 4 cores
- **RAM:** 8GB
- **Model:** `llama3.2:3b`
- **Chunk size:** 1000
- **Expected speed:** ~30s per chunk

### Recommended (GPU)
- **CPU:** 6+ cores
- **RAM:** 16GB
- **GPU:** NVIDIA GTX 1660+ (6GB VRAM) or equivalent
- **Model:** `qwen2.5:7b`
- **Chunk size:** 2000
- **Expected speed:** ~5-10s per chunk

### Optimal (High-end GPU)
- **CPU:** 8+ cores
- **RAM:** 32GB
- **GPU:** NVIDIA RTX 3060+ (12GB VRAM) or higher
- **Model:** `qwen3:8b` or larger
- **Chunk size:** 3000
- **Expected speed:** ~3-5s per chunk

## Troubleshooting Commands

### Check Ollama Status
```bash
ollama ps
```

### Check Available Models
```bash
ollama list
```

### Test Model Speed
```bash
time ollama run qwen2.5:7b "Translate to Chinese: Hello World"
```

### Monitor System Resources

**Windows:**
```powershell
# Task Manager: Ctrl+Shift+Esc
# Or use PowerShell:
Get-Counter '\Processor(_Total)\% Processor Time'
```

**Linux/Mac:**
```bash
htop
# Or
top
```

### Check GPU Usage (NVIDIA)
```bash
nvidia-smi
```

## Performance Tuning Tips

### 1. Pre-load Model

Start Ollama with your model before translation:
```bash
ollama run qwen2.5:7b
# Press Ctrl+D to exit chat but keep model loaded
```

### 2. Use Keep-Alive

Configure Ollama to keep models in memory:
```bash
# In ~/.ollama/config.json (create if doesn't exist)
{
  "keep_alive": "5m"
}
```

### 3. Batch Processing

Process multiple files sequentially instead of parallel to avoid memory issues.

### 4. Monitor and Adjust

Start with conservative settings and gradually increase:
1. Start: `chunk_size: 1000, timeout: 600`
2. If successful: `chunk_size: 1500, timeout: 450`
3. If successful: `chunk_size: 2000, timeout: 300`

## Expected Translation Times

For a 12,000 character document split into 6 chunks:

| Configuration | Total Time | Per Chunk |
|---------------|------------|-----------|
| `llama3.2:3b` (CPU) | ~3-5 min | ~30-50s |
| `qwen2.5:7b` (CPU) | ~5-10 min | ~50-100s |
| `qwen2.5:7b` (GPU) | ~1-2 min | ~10-20s |
| `qwen3:8b` (GPU) | ~2-3 min | ~20-30s |
| `gpt-4o-mini` (API) | ~30-60s | ~5-10s |

## When to Use Cloud APIs

Consider using OpenAI or Gemini APIs when:
- Your hardware is limited (CPU only, < 8GB RAM)
- You need fast results
- You don't need offline capability
- Cost is acceptable (~$0.15 per million tokens)

Example cost: Translating 10,000 chars ≈ 3,000 tokens ≈ $0.0005

## Best Practices

1. **Test with small files first** - Before processing large documents
2. **Use appropriate chunk sizes** - Balance between speed and context
3. **Monitor system resources** - Ensure system stability
4. **Choose right model for task** - Speed vs Quality trade-off
5. **Consider cloud APIs for production** - More reliable and faster
6. **Save failed chunks** - Implement partial resume (future feature)

## Getting Help

If you continue to experience issues:

1. Check Ollama logs:
   ```bash
   # Linux/Mac
   journalctl -u ollama
   
   # Windows
   # Check Event Viewer or Ollama service logs
   ```

2. Verify model is working:
   ```bash
   ollama run qwen2.5:7b "Hello"
   ```

3. Check translation logs in `log/translation_*.log`

4. Try a different model or cloud API

5. Report issues with:
   - System specs (CPU, RAM, GPU)
   - Model name and size
   - Configuration used
   - Error messages from logs
