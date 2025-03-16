@echo off
:: call setEnv.bat
setlocal EnableDelayedExpansion

:: Set UTF-8 encoding
chcp 65001 >nul

:: Define the batch_files directory inside the project root
for %%I in ("%~dp0..") do set "project_root=%%~fI"
set "batch_files_dir=%project_root%\batch_files"
set "source_files=%batch_files_dir%\source_files.txt"
set "chunks_json=%batch_files_dir%\chunks.json"

:: Ensure batch_files directory exists
if not exist "%batch_files_dir%" (
    echo Error: batch_files directory not found: %batch_files_dir%
    exit /b 1
)

:: Check if source_files.txt exists in batch_files
if not exist "%source_files%" (
    echo Error: source_files.txt not found in %batch_files_dir%
    exit /b 1
)

:: Check if required tools are available
where curl >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: curl is not installed or not in PATH. Please install curl.
    exit /b 1
)

:: Check if environment variables are set
if "%GH_OWNER%"=="" (
    echo Error: Environment variable GH_OWNER is not set.
    exit /b 1
)
if "%GH_REPO%"=="" (
    echo Error: Environment variable GH_REPO is not set.
    exit /b 1
)
if "%GH_BRANCH%"=="" (
    echo Error: Environment variable GH_BRANCH is not set.
    exit /b 1
)

:: Initialize chunks.json inside batch_files
echo { > "%chunks_json%"

set "first_entry=1"

:: Read source_files.txt from batch_files directory
for /f "usebackq tokens=*" %%i in ("%source_files%") do (
    set "filePath=%%i"
    echo -----------------------------------------
    echo Processing: !filePath!
    echo GH_OWNER  = %GH_OWNER%
    echo GH_REPO   = %GH_REPO%
    echo GH_BRANCH = %GH_BRANCH%

    set "api_path=%%i"
    set "api_path=!api_path:\=/!"
    set "escaped_path=!api_path!"

    echo API Path: !escaped_path!

    :: Fetch the response
    curl -k -G -s "https://devdocs-vftt.onrender.com/parseCode" ^
        --data-urlencode "owner=%GH_OWNER%" ^
        --data-urlencode "repo=%GH_REPO%" ^
        --data-urlencode "branch=%GH_BRANCH%" ^
        --data-urlencode "filePath=!escaped_path!" ^
        --verbose -o temp.json

    echo API Response for !filePath!:
    type temp.json
    echo.

    set "json_key=!filePath!"
    set "json_key=!json_key:\=\\!"

    if exist "temp.json" (
        for %%F in ("temp.json") do set "size=%%~zF"
        if !size! gtr 0 (
            if !first_entry! equ 1 (
                echo   "!json_key!": >> "%chunks_json%"
                type temp.json >> "%chunks_json%"
                set "first_entry=0"
            ) else (
                echo   , "!json_key!": >> "%chunks_json%"
                type temp.json >> "%chunks_json%"
            )
        ) else (
            if !first_entry! equ 1 (
                echo   "!json_key!": {"error": "Empty response from API"} >> "%chunks_json%"
                set "first_entry=0"
            ) else (
                echo   , "!json_key!": {"error": "Empty response from API"} >> "%chunks_json%"
            )
        )
    ) else (
        if !first_entry! equ 1 (
            echo   "!json_key!": {"error": "API call failed"} >> "%chunks_json%"
            set "first_entry=0"
        ) else (
            echo   , "!json_key!": {"error": "API call failed"} >> "%chunks_json%"
        )
    )

    if exist "temp.json" del "temp.json"
)

echo } >> "%chunks_json%"
echo Done! Results written to %chunks_json%
endlocal
exit /b 0
