@echo off
setlocal enabledelayedexpansion

REM Get the project root (assuming batch file is in a subfolder of project root)
for %%I in ("%~dp0..") do set "project_root=%%~fI"
echo Project root set to: %project_root%

REM Verify the project root exists
if not exist "%project_root%" (
    echo ERROR: Project root directory does not exist: %project_root%
    pause
    exit /b 1
)

REM Define batch_files directory inside project root
set "batch_files_dir=%project_root%\batch_files"

REM Ensure batch_files directory exists
if not exist "%batch_files_dir%" mkdir "%batch_files_dir%"

REM Define output file inside batch_files
set "output_file=%batch_files_dir%\source_files.txt"

REM Clear the output file if it already exists
type nul > "%output_file%"

REM Find all .java and .py files and store their paths relative to project root
for /r "%project_root%" %%f in (*.java *.py) do (
    set "full_path=%%f"
    set "relative_path=!full_path:%project_root%\=!"

    REM Convert backslashes to forward slashes
    set "relative_path=!relative_path:\=/!"

    echo(!relative_path! >> "%output_file%"
)

REM Check if anything was written
if %errorlevel% neq 0 (
    echo ERROR: No .java or .py files found or issue with writing to %output_file%
) else (
    echo Paths of all .java and .py files have been stored in %output_file%
    echo Full path: %output_file%
)

endlocal