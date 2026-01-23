"""Diagnostic script for translation performance issues"""

import asyncio
import time
import httpx
from pathlib import Path


async def test_ollama_connection():
    """Test if Ollama is accessible"""
    print("\n" + "="*60)
    print("1. Testing Ollama Connection")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:11434/api/version")
            if response.status_code == 200:
                version_info = response.json()
                print("✓ Ollama is running")
                print(f"  Version: {version_info.get('version', 'unknown')}")
                return True
            else:
                print(f"✗ Ollama returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("\nSolution:")
        print("  1. Make sure Ollama is installed")
        print("  2. Run: ollama serve")
        return False


async def test_model_availability(model: str = "qwen2.5:7b"):
    """Test if model is available"""
    print("\n" + "="*60)
    print("2. Testing Model Availability")
    print("="*60)
    print(f"Checking model: {model}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models_info = response.json()
                models = [m['name'] for m in models_info.get('models', [])]
                
                print(f"\nAvailable models ({len(models)}):")
                for m in models:
                    marker = "✓" if model in m else " "
                    print(f"  {marker} {m}")
                
                if any(model in m for m in models):
                    print(f"\n✓ Model '{model}' is available")
                    return True
                else:
                    print(f"\n✗ Model '{model}' not found")
                    print(f"\nSolution:")
                    print(f"  Run: ollama pull {model}")
                    return False
            else:
                print(f"✗ Cannot list models: status {response.status_code}")
                return False
    except Exception as e:
        print(f"✗ Error checking models: {e}")
        return False


async def test_translation_speed(model: str = "qwen2.5:7b"):
    """Test actual translation speed"""
    print("\n" + "="*60)
    print("3. Testing Translation Speed")
    print("="*60)
    
    test_text = """# Test Document

This is a simple test document to measure translation speed.

## Features

- Short paragraphs
- Simple structure
- Easy to translate

This helps us estimate performance."""
    
    print(f"Test text length: {len(test_text)} characters")
    print(f"Model: {model}")
    print("\nStarting translation test...")
    
    prompt = f"Translate this to Chinese, keep Markdown format:\n\n{test_text}"
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }
    
    try:
        start_time = time.time()
        
        timeout = httpx.Timeout(
            connect=30.0,
            read=120.0,  # 2 minutes for test
            write=30.0,
            pool=30.0
        )
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "http://localhost:11434/v1/chat/completions",
                json=data
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                translated = result["choices"][0]["message"]["content"]
                
                print(f"\n✓ Translation completed in {elapsed:.1f} seconds")
                print(f"  Input: {len(test_text)} chars")
                print(f"  Output: {len(translated)} chars")
                print(f"  Speed: {len(test_text) / elapsed:.0f} chars/second")
                
                # Estimate time for actual document
                print("\n" + "-"*60)
                print("Estimated time for 12,000 char document:")
                doc_size = 12000
                chunk_size = 1500
                chunks = (doc_size + chunk_size - 1) // chunk_size
                time_per_chunk = elapsed * (chunk_size / len(test_text))
                total_time = time_per_chunk * chunks
                
                print(f"  Chunk size: {chunk_size} chars")
                print(f"  Number of chunks: {chunks}")
                print(f"  Time per chunk: ~{time_per_chunk:.0f}s")
                print(f"  Total time: ~{total_time/60:.1f} minutes")
                print("-"*60)
                
                if elapsed > 30:
                    print("\n⚠ Warning: Translation is slow")
                    print("  Consider:")
                    print("  - Using a smaller model (llama3.2:3b)")
                    print("  - Enabling GPU acceleration")
                    print("  - Using cloud APIs (OpenAI/Gemini)")
                
                return True
            else:
                print(f"\n✗ Translation failed: status {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return False
                
    except httpx.TimeoutException:
        elapsed = time.time() - start_time
        print(f"\n✗ Translation timed out after {elapsed:.1f} seconds")
        print("\nThis model is too slow for your hardware.")
        print("\nRecommendations:")
        print("  1. Use a faster model:")
        print("     ollama pull llama3.2:3b")
        print("  2. Enable GPU acceleration")
        print("  3. Use cloud APIs (OpenAI/Gemini)")
        return False
        
    except Exception as e:
        print(f"\n✗ Translation test failed: {e}")
        return False


def check_system_resources():
    """Check system resources"""
    print("\n" + "="*60)
    print("4. System Resources")
    print("="*60)
    
    try:
        import psutil
        
        # CPU
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"CPU: {cpu_count} cores, {cpu_percent}% usage")
        
        # RAM
        mem = psutil.virtual_memory()
        print(f"RAM: {mem.total / (1024**3):.1f}GB total, "
              f"{mem.available / (1024**3):.1f}GB available "
              f"({mem.percent}% used)")
        
        # Disk
        disk = psutil.disk_usage('.')
        print(f"Disk: {disk.free / (1024**3):.1f}GB free")
        
        # Recommendations
        print("\n" + "-"*60)
        if mem.available < 4 * (1024**3):  # Less than 4GB
            print("⚠ Low memory available")
            print("  Consider using smaller models or cloud APIs")
        
        if cpu_count < 4:
            print("⚠ Limited CPU cores")
            print("  Translation may be slow, consider cloud APIs")
        
        if cpu_percent > 80:
            print("⚠ High CPU usage")
            print("  Close other applications before translating")
        
        print("-"*60)
        
    except ImportError:
        print("(Install psutil for detailed system info: pip install psutil)")


def print_recommendations():
    """Print optimization recommendations"""
    print("\n" + "="*60)
    print("Recommendations")
    print("="*60)
    
    print("""
Based on performance testing, here are the recommended configurations:

1. For Fast Translation (Recommended for most users):
   {
     "provider": "ollama",
     "model": "llama3.2:3b",
     "chunk_size": 1000,
     "timeout": 300
   }

2. For Better Quality (if you have good hardware):
   {
     "provider": "ollama",
     "model": "qwen2.5:7b",
     "chunk_size": 1500,
     "timeout": 600
   }

3. For Best Performance (use cloud API):
   {
     "provider": "openai",
     "api_key": "your-key",
     "model": "gpt-4o-mini",
     "chunk_size": 3000,
     "timeout": 120
   }

For more details, see TRANSLATION_PERFORMANCE.md
    """)


async def main():
    """Run all diagnostic tests"""
    print("="*60)
    print("URL2MD Translation Performance Diagnostic")
    print("="*60)
    print("\nThis tool will help identify translation performance issues.")
    
    # Test 1: Connection
    if not await test_ollama_connection():
        print("\n❌ Cannot proceed without Ollama connection")
        return
    
    # Test 2: Model availability
    model = input("\nEnter model name to test (default: qwen2.5:7b): ").strip()
    if not model:
        model = "qwen2.5:7b"
    
    if not await test_model_availability(model):
        print("\n❌ Cannot proceed without model")
        return
    
    # Test 3: Speed test
    print("\nThis will run a translation test (may take 30-120 seconds)")
    proceed = input("Continue? (y/n): ").strip().lower()
    if proceed == 'y':
        await test_translation_speed(model)
    
    # Test 4: System resources
    check_system_resources()
    
    # Print recommendations
    print_recommendations()
    
    print("\n" + "="*60)
    print("Diagnostic Complete")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
