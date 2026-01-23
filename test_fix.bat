@echo off
REM Quick test to verify translation fixes

echo ========================================
echo Testing Translation Fixes
echo ========================================
echo.

echo This will test the translation with optimized settings.
echo.

REM Create a small test file
echo Creating test file...
echo # Test Document > test_small.md
echo. >> test_small.md
echo This is a test. >> test_small.md
echo. >> test_small.md
echo ## Features >> test_small.md
echo. >> test_small.md
echo - Fast translation >> test_small.md
echo - Better error handling >> test_small.md

echo.
echo Test file created: test_small.md
echo.

echo Running diagnostic tool...
echo.
uv run python diagnose_translation.py

echo.
echo ========================================
echo Done!
echo ========================================
echo.
echo To test actual translation, run:
echo uv run url2md YOUR_URL --auto-translate --provider ollama --model llama3.2:3b
echo.

pause
