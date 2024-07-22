' Set WshShell = CreateObject("WScript.Shell")
' WshShell.Run chr(34) & "C:\Users\Owner\Documents\olmismis\run_app.bat" & chr(34), 1, true
' Set WshShell = Nothing

Option Explicit

Dim shell, fso, logFile, scriptLogFile, serverLogFile, serverPid, checkServer, pythonExePath

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

logFile = "server_log.txt"
scriptLogFile = "script_log.txt"
serverLogFile = "server_log.txt"
pythonExePath = "C:\Users\Owner\Documents\olmismis\venv\Scripts\python.exe"

' Clear the log files
If fso.FileExists(logFile) Then fso.DeleteFile(logFile)
If fso.FileExists(scriptLogFile) Then fso.DeleteFile(scriptLogFile)

WriteLog "Starting the script..."

' Activate virtual environment
WriteLog "Activating virtual environment..."
TryCommand "cmd /c C:\Users\Owner\Documents\olmismis\venv\Scripts\activate.bat"

' Start Django server
WriteLog "Starting Django server..."
TryCommand "cmd /c start /B """ & pythonExePath & """ C:\Users\Owner\Documents\olmismis\manage.py runserver > """ & serverLogFile & """ 2>&1"

' Wait for server to start
WriteLog "Waiting for server to start..."
Do
    WScript.Sleep 10000 ' Wait 10 seconds
    checkServer = shell.Run("cmd /c curl -s http://127.0.0.1:8000/ > nul 2>&1", 0, True)
Loop While checkServer <> 0

WriteLog "Django server started successfully."

' Open the browser
WriteLog "Opening the browser..."
shell.Run "chrome.exe http://127.0.0.1:8000/", 0, False

' Get the process ID of the Python server
serverPid = GetProcessID("python.exe")

If serverPid = "" Then
    WriteLog "Failed to get the Django server PID."
Else
    WriteLog "Django Server PID is " & serverPid
End If

' Monitor the Django server process
Do
    WScript.Sleep 1000 ' Wait 1 second
Loop While IsProcessRunning(serverPid)

WriteLog "Script completed successfully."

' Log the completion time
LogCompletionTime

' Helper Functions
Sub WriteLog(message)
    Dim file
    Set file = fso.OpenTextFile(scriptLogFile, 8, True)
    file.WriteLine Now & " - " & message
    file.Close
End Sub

Sub LogCompletionTime
    Dim file
    Set file = fso.OpenTextFile(scriptLogFile, 8, True)
    file.WriteLine "Script completed at " & Now
    file.Close
End Sub

Sub TryCommand(command)
    Dim result
    result = shell.Run(command, 0, True) ' Window style 0 to hide the command prompt
    If result <> 0 Then
        WriteLog "Command failed: " & command
        WriteLog "Script failed at " & Now
        WScript.Quit 1
    End If
End Sub

Function GetProcessID(processName)
    Dim command, result, lines, line, parts
    command = "tasklist /fi ""IMAGENAME eq " & processName & """ /fo csv /nh"
    result = shell.Exec("cmd /c " & command).StdOut.ReadAll
    lines = Split(result, vbCrLf)
    If UBound(lines) >= 0 Then
        line = lines(0)
        parts = Split(line, ",")
        If UBound(parts) >= 1 Then
            GetProcessID = Replace(parts(1), """", "")
        End If
    End Function

Function IsProcessRunning(pid)
    Dim command, result
    command = "tasklist /fi ""PID eq " & pid & """ /fo csv /nh"
    result = shell.Exec("cmd /c " & command).StdOut.ReadAll
    IsProcessRunning = (InStr(result, "No tasks") = 0)
End Function
