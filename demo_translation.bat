@echo off
REM Example: Convert and translate a webpage using Ollama (local)

echo ========================================
echo URL2MD Translation Demo
echo ========================================
echo.

echo This script will:
echo 1. Convert a webpage to Markdown
echo 2. Translate it to Chinese using Ollama
echo.

echo Prerequisites:
echo - Ollama must be installed and running
echo - Run: ollama serve
echo - Run: ollama pull llama3.2
echo.

pause

echo.
echo Starting conversion and translation...
echo.

REM Example URL - you can change this
set URL=https://docs.python.org/3/tutorial/introduction.html

REM Run conversion with auto-translation
uv run url2md %URL% --auto-translate --provider ollama --target-language Chinese --verbose

echo.
echo ========================================
echo Done!
echo ========================================
echo.
echo Check the outputs/ folder for:
echo - Original Markdown file
echo - Translated Markdown file (with _zh suffix)
echo.
echo Check the log/ folder for translation logs.
echo.

pause
