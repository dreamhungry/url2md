"""Translation agent for converting Markdown files to different languages"""

import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Literal
import httpx
from datetime import datetime


class TranslationConfig:
    """Configuration for translation API"""
    
    def __init__(
        self,
        provider: Literal["openai", "gemini", "ollama"] = "openai",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        target_language: str = "Chinese",
        chunk_size: int = 3000,
        timeout: int = 120,
    ):
        """Initialize translation configuration
        
        Args:
            provider: API provider ("openai", "gemini", or "ollama")
            api_key: API key (not needed for ollama)
            api_base: API base URL (e.g., "http://localhost:11434" for ollama)
            model: Model name (e.g., "gpt-4o-mini", "gemini-pro", "llama3")
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            target_language: Target language for translation
            chunk_size: Characters per chunk for large documents
            timeout: Request timeout in seconds
        """
        self.provider = provider
        self.api_key = api_key
        self.target_language = target_language
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.chunk_size = chunk_size
        self.timeout = timeout
        
        # Set default model and API base based on provider
        if model is None:
            self.model = self._get_default_model(provider)
        else:
            self.model = model
            
        if api_base is None:
            self.api_base = self._get_default_api_base(provider)
        else:
            self.api_base = api_base
    
    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider"""
        defaults = {
            "openai": "gpt-4o-mini",
            "gemini": "gemini-2.0-flash-exp",
            "ollama": "llama3.2",
        }
        return defaults.get(provider, "gpt-4o-mini")
    
    def _get_default_api_base(self, provider: str) -> str:
        """Get default API base URL for provider"""
        defaults = {
            "openai": "https://api.openai.com/v1",
            "gemini": "https://generativelanguage.googleapis.com/v1beta",
            "ollama": "http://localhost:11434/v1",
        }
        return defaults.get(provider, "https://api.openai.com/v1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "provider": self.provider,
            "model": self.model,
            "api_base": self.api_base,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "target_language": self.target_language,
            "chunk_size": self.chunk_size,
            "timeout": self.timeout,
        }


class TranslationAgent:
    """Agent for translating Markdown files using various LLM APIs"""
    
    def __init__(self, config: TranslationConfig):
        """Initialize translation agent
        
        Args:
            config: Translation configuration
        """
        self.config = config
        self.log_messages = []
    
    def _log(self, message: str):
        """Add log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        print(log_entry)
    
    def _create_translation_prompt(self, content: str) -> str:
        """Create translation prompt
        
        Args:
            content: Markdown content to translate
            
        Returns:
            Translation prompt
        """
        return f"""Translate this Markdown to {self.config.target_language}.

Rules:
1. Keep all Markdown formatting (headers, links, code blocks, lists)
2. Don't translate: code blocks, URLs, HTML tags
3. Keep original structure
4. Output only the translated Markdown

{content}"""
    
    def _split_content(self, content: str) -> list[str]:
        """Split content into chunks for translation
        
        Args:
            content: Full markdown content
            
        Returns:
            List of content chunks
        """
        # If content is small enough, return as single chunk
        if len(content) <= self.config.chunk_size:
            return [content]
        
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_length = 0
        
        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            
            # If adding this line exceeds chunk size, start new chunk
            if current_length + line_length > self.config.chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = line_length
            else:
                current_chunk.append(line)
                current_length += line_length
        
        # Add remaining content
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI-compatible API
        
        Args:
            prompt: Translation prompt
            
        Returns:
            Translated text
        """
        headers = {
            "Content-Type": "application/json",
        }
        
        # Add API key if provided (not needed for local ollama)
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.temperature,
        }
        
        if self.config.max_tokens:
            data["max_tokens"] = self.config.max_tokens
        
        url = f"{self.config.api_base}/chat/completions"
        
        # Create timeout configuration with separate read timeout
        timeout = httpx.Timeout(
            connect=30.0,  # Connection timeout
            read=self.config.timeout,  # Read timeout (for response)
            write=30.0,  # Write timeout
            pool=30.0  # Pool timeout
        )
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                
                return result["choices"][0]["message"]["content"].strip()
            except httpx.TimeoutException as e:
                self._log(f"✗ Timeout error: {e}")
                raise Exception(f"Translation request timed out after {self.config.timeout}s. Try reducing chunk_size or increasing timeout.")
            except httpx.HTTPStatusError as e:
                self._log(f"✗ HTTP error {e.response.status_code}: {e.response.text}")
                raise Exception(f"API returned error {e.response.status_code}: {e.response.text[:200]}")
            except Exception as e:
                self._log(f"✗ Unexpected error: {e}")
                raise
    
    async def _call_gemini_api(self, prompt: str) -> str:
        """Call Google Gemini API
        
        Args:
            prompt: Translation prompt
            
        Returns:
            Translated text
        """
        if not self.config.api_key:
            raise ValueError("API key is required for Gemini API")
        
        url = f"{self.config.api_base}/models/{self.config.model}:generateContent"
        params = {"key": self.config.api_key}
        
        headers = {
            "Content-Type": "application/json",
        }
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": self.config.temperature,
            }
        }
        
        if self.config.max_tokens:
            data["generationConfig"]["maxOutputTokens"] = self.config.max_tokens
        
        # Create timeout configuration
        timeout = httpx.Timeout(
            connect=30.0,
            read=self.config.timeout,
            write=30.0,
            pool=30.0
        )
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(url, params=params, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                
                return result["candidates"][0]["content"]["parts"][0]["text"].strip()
            except httpx.TimeoutException as e:
                self._log(f"✗ Timeout error: {e}")
                raise Exception(f"Translation request timed out after {self.config.timeout}s")
            except httpx.HTTPStatusError as e:
                self._log(f"✗ HTTP error {e.response.status_code}: {e.response.text}")
                raise Exception(f"API returned error {e.response.status_code}: {e.response.text[:200]}")
            except Exception as e:
                self._log(f"✗ Unexpected error: {e}")
                raise
    
    async def _translate_chunk(self, chunk: str, chunk_num: int, total_chunks: int) -> str:
        """Translate a single chunk with retry mechanism
        
        Args:
            chunk: Content chunk to translate
            chunk_num: Current chunk number
            total_chunks: Total number of chunks
            
        Returns:
            Translated chunk
        """
        self._log(f"Translating chunk {chunk_num}/{total_chunks} ({len(chunk)} chars)...")
        
        prompt = self._create_translation_prompt(chunk)
        
        # Retry mechanism for transient failures
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                # Call appropriate API based on provider
                if self.config.provider == "gemini":
                    translated = await self._call_gemini_api(prompt)
                else:
                    # Both OpenAI and Ollama use OpenAI-compatible API
                    translated = await self._call_openai_api(prompt)
                
                self._log(f"✓ Chunk {chunk_num}/{total_chunks} translated ({len(translated)} chars)")
                return translated
                
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 5  # 5s, 10s
                    self._log(f"⚠ Attempt {attempt + 1} failed: {str(e)[:100]}")
                    self._log(f"  Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    self._log(f"✗ All {max_retries + 1} attempts failed for chunk {chunk_num}")
        
        # If all retries failed
        raise Exception(f"Failed to translate chunk {chunk_num}/{total_chunks} after {max_retries + 1} attempts: {last_error}")
    
    async def translate_file(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Translate a Markdown file
        
        Args:
            input_path: Path to input Markdown file
            output_path: Path to output file (optional, auto-generated if not provided)
            
        Returns:
            Path to translated file
        """
        self._log(f"Starting translation: {input_path}")
        self._log(f"Config: {json.dumps(self.config.to_dict(), indent=2)}")
        
        # Read input file
        content = input_path.read_text(encoding='utf-8')
        self._log(f"Loaded file: {len(content)} characters")
        
        # Split into chunks if needed
        chunks = self._split_content(content)
        total_chunks = len(chunks)
        
        if total_chunks > 1:
            self._log(f"Split into {total_chunks} chunks for translation")
        
        # Translate each chunk
        translated_chunks = []
        for i, chunk in enumerate(chunks, 1):
            translated_chunk = await self._translate_chunk(chunk, i, total_chunks)
            translated_chunks.append(translated_chunk)
        
        # Combine translated chunks
        translated_content = '\n\n'.join(translated_chunks)
        
        # Generate output path if not provided
        if output_path is None:
            stem = input_path.stem
            suffix = input_path.suffix
            lang_code = self._get_language_code(self.config.target_language)
            output_path = input_path.parent / f"{stem}_{lang_code}{suffix}"
        
        # Save translated content
        output_path.write_text(translated_content, encoding='utf-8')
        self._log(f"✓ Translation completed: {output_path}")
        self._log(f"Output size: {len(translated_content)} characters")
        
        return output_path
    
    def _get_language_code(self, language: str) -> str:
        """Get language code for filename
        
        Args:
            language: Language name
            
        Returns:
            Language code
        """
        language_lower = language.lower()
        
        codes = {
            "chinese": "zh",
            "简体中文": "zh",
            "中文": "zh",
            "english": "en",
            "japanese": "ja",
            "日语": "ja",
            "korean": "ko",
            "韩语": "ko",
            "french": "fr",
            "german": "de",
            "spanish": "es",
        }
        
        return codes.get(language_lower, "translated")
    
    def save_log(self, log_path: Path):
        """Save translation log to file
        
        Args:
            log_path: Path to save log file
        """
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_content = '\n'.join(self.log_messages)
        log_path.write_text(log_content, encoding='utf-8')


def confirm_translation(target_language: str = "Chinese") -> bool:
    """Ask user to confirm translation
    
    Args:
        target_language: Target language
        
    Returns:
        True if user confirms, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Translation Option")
    print(f"{'='*60}")
    print(f"Target Language: {target_language}")
    print(f"{'='*60}")
    
    while True:
        response = input("Do you want to translate this document? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")


async def translate_markdown_file(
    input_path: Path,
    config: Optional[TranslationConfig] = None,
    auto_translate: bool = False,
    output_path: Optional[Path] = None,
) -> Optional[Path]:
    """Translate a Markdown file with confirmation
    
    Args:
        input_path: Path to input Markdown file
        config: Translation configuration (uses default if not provided)
        auto_translate: If True, skip confirmation
        output_path: Path to output file (optional)
        
    Returns:
        Path to translated file, or None if translation was cancelled
    """
    # Use default config if not provided
    if config is None:
        config = TranslationConfig()
    
    # Ask for confirmation if not auto-translating
    if not auto_translate:
        if not confirm_translation(config.target_language):
            print("Translation cancelled by user.")
            return None
    
    # Create translator and translate
    translator = TranslationAgent(config)
    
    try:
        translated_path = await translator.translate_file(input_path, output_path)
        
        # Save translation log
        log_dir = Path("log")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = log_dir / f"translation_{timestamp}.log"
        translator.save_log(log_path)
        
        return translated_path
    
    except Exception as e:
        print(f"\nTranslation failed: {e}")
        raise
