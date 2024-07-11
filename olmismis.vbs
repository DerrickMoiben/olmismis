Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "C:\Users\Owner\Documents\olmismis\run_app.bat" & chr(34), 1, true
Set WshShell = Nothing
