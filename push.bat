@echo off
setlocal enabledelayedexpansion

REM Check if commit message was provided
if "%~1"=="" (
    echo Error: Please provide a commit message
    echo Usage: push.bat "your commit message"
    exit /b 1
)

REM Get the commit message (supports spaces)
set "commit_message=%~1"

echo ================================
echo Git Push Script
echo ================================
echo.

REM Check git status
echo Checking git status...
git status
echo.

REM Add all changes
echo Adding all changes...
git add .
echo.

REM Commit with provided message
echo Committing changes...
git commit -m "%commit_message%"
echo.

REM Push to remote
echo Pushing to remote repository...
git push
echo.

if errorlevel 1 (
    echo.
    echo Error occurred during push!
    pause
    exit /b 1
) else (
    echo.
    echo ================================
    echo Successfully pushed to remote!
    echo ================================
    echo.
)

endlocal
