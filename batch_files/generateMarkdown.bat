@echo off
setlocal EnableDelayedExpansion

REM Define paths
set "BATCH_DIR=%~dp0"
set "INPUT_FILE=%BATCH_DIR%output.json"
set "OUTPUT_DIR=%BATCH_DIR%..\docs"
set "IMAGE_DIR=%OUTPUT_DIR%\images"

REM Ensure the docs and images directories exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%IMAGE_DIR%" mkdir "%IMAGE_DIR%"

REM Check if JSON file exists
if not exist "%INPUT_FILE%" (
    echo Error: JSON file not found at %INPUT_FILE%
    exit /b 1
)

REM Read JSON and create markdown files
powershell -NoProfile -ExecutionPolicy Bypass -File "%BATCH_DIR%process_json.ps1" "%INPUT_FILE%" "%OUTPUT_DIR%" "%IMAGE_DIR%"

REM Check for errors
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to parse JSON or create markdown files.
    exit /b 1
)

echo Markdown files created successfully in %OUTPUT_DIR%
echo Extracted images saved in %IMAGE_DIR%
exit /b 0
