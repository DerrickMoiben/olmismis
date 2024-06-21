@echo off
cls

echo Starting the script...

REM Activate virtual environment and start the Django server in the background
echo Activating virtual environment...
call C:\Users\Owner\Documents\olmismis\venv\Scripts\activate

if errorlevel 1 (
    echo Failed to activate virtual environment. Check the path and try again. >> server_log.txt
    echo Script failed at %date% %time% >> script_log.txt
    exit /b 1
)

echo Starting Django server...
start "" /B cmd /c "python C:\Users\Owner\Documents\olmismis\manage.py runserver > server_log.txt 2>&1"

REM Wait for the server to start by checking the availability of the URL
echo Waiting for server to start...
:waitForServer
timeout /t 10 >nul
curl -s http://127.0.0.1:8000/ >nul 2>&1
if errorlevel 1 goto waitForServer

echo Django server started successfully.

REM Open the browser and get the process ID
echo Opening the browser...
start chrome.exe http://127.0.0.1:8000/
timeout /t 5 >nul

REM Get the process ID of the browser
for /f "tokens=2 delims=," %%a in ('tasklist /fi "IMAGENAME eq chrome.exe" /fo csv /nh') do set browser_pid=%%a
echo Browser PID is %browser_pid%

REM Monitor the browser process and wait until it exits
:waitForBrowser
timeout /t 1 >nul
tasklist /fi "PID eq %browser_pid%" | find /i "chrome.exe" >nul
if not errorlevel 1 goto waitForBrowser

REM Stop the Django server
echo Stopping Django server...
taskkill /f /im python.exe

REM Log completion
echo Script completed at %date% %time% >> script_log.txt
echo Script completed successfully.
