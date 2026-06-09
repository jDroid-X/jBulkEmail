' jBES Enterprise Mission Setup Wizard
' MISSION: Professional Sequential Installation (Windows Standard Style)
' VERSION: 6.5-ENTERPRISE-SETUP

Set objShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
Set objSA = CreateObject("Shell.Application")

strAppTitle = "jBES Discovery v6.5 Setup"
strSource = fso.GetParentFolderName(WScript.ScriptFullName)

' --- STEP 1: WELCOME SCREEN ---
strMsg = "Welcome to the jBES Discovery Setup Wizard." & vbCrLf & vbCrLf & _
         "This program will install jBulkEmailSender on your computer." & vbCrLf & vbCrLf & _
         "It is recommended that you close all other applications before continuing." & vbCrLf & vbCrLf & _
         "Click OK to continue, or Cancel to exit Setup."
         
If MsgBox(strMsg, 1 + 64, strAppTitle) = 2 Then WScript.Quit

' --- STEP 2: SELECT DESTINATION LOCATION ---
strDefaultPath = objShell.ExpandEnvironmentStrings("%LocalAppData%") & "\Programs\jBES_Discovery"
strMsg = "Select Destination Location" & vbCrLf & vbCrLf & _
         "Setup will install jBulkEmailSender into the following folder." & vbCrLf & vbCrLf & _
         "To continue, click OK. If you would like to select a different folder, click YES to browse."

res = MsgBox(strMsg & vbCrLf & vbCrLf & strDefaultPath, 3 + 64, strAppTitle)
If res = 2 Then WScript.Quit ' Cancel

strInstallPath = strDefaultPath
If res = 6 Then ' Yes (Browse)
    Set objFolder = objSA.BrowseForFolder(0, "Select Destination Folder", 0, 16)
    If Not objFolder Is Nothing Then
        strInstallPath = objFolder.Self.Path
        If fso.GetFileName(strInstallPath) <> "jBES_Discovery" Then
            strInstallPath = strInstallPath & "\jBES_Discovery"
        End If
    Else
        MsgBox "No folder selected. Setup will use default path.", 48, strAppTitle
    End If
End If

' --- STEP 3: PRE-INSTALLATION SUMMARY (READY TO INSTALL) ---
strComponents = "- Core Transmission Engine" & vbCrLf & _
                "- Tactical Asset Library (Icons/UI)" & vbCrLf & _
                "- Python Portability Layer" & vbCrLf & _
                "- Microsoft Compliance Logic"

strSummary = "Ready to Install" & vbCrLf & vbCrLf & _
             "Setup is now ready to begin installing jBulkEmailSender on your computer." & vbCrLf & vbCrLf & _
             "Destination Location:" & vbCrLf & "  " & strInstallPath & vbCrLf & vbCrLf & _
             "Selected Components:" & vbCrLf & strComponents & vbCrLf & vbCrLf & _
             "Click OK to proceed with the installation."

If MsgBox(strSummary, 1 + 64, strAppTitle) = 2 Then WScript.Quit

' --- STEP 4: INSTALLATION (COPYING FILES) ---
' Create directories
If Not fso.FolderExists(strInstallPath) Then
    objShell.Run "cmd /c mkdir " & Chr(34) & strInstallPath & Chr(34), 0, True
End If

' Define Mission Assets
sub_folders = Array("assets", "core", "app")
core_files = Array("jBulkEmailSender.exe", "bulk_email_sender.py", "main.py", "requirements.txt", "BulkEmailSender.bat")

objShell.Popup "Installing... Please wait while Setup installs jBulkEmailSender on your computer.", 1, strAppTitle, 64

strLog = ""
intCount = 0

' Deploy Folders
For Each folder In sub_folders
    src = strSource & "\" & folder
    If fso.FolderExists(src) Then
        fso.CopyFolder src, strInstallPath & "\", True
        strLog = strLog & "  [Folder] " & folder & " -> Deployed" & vbCrLf
        intCount = intCount + 1
    End If
Next

' Deploy Files
For Each file In core_files
    src = strSource & "\" & file
    If fso.FileExists(src) Then
        fso.CopyFile src, strInstallPath & "\", True
        strLog = strLog & "  [File] " & file & " -> Deployed" & vbCrLf
        intCount = intCount + 1
    End If
Next

If intCount = 0 Then
    MsgBox "Setup failed to locate installation source files in:" & vbCrLf & strSource, 16, "Setup Error"
    WScript.Quit
End If

' --- STEP 5: SHORTCUT OPTIONS ---
strMsg = "Select Additional Tasks" & vbCrLf & vbCrLf & _
         "Which additional tasks should Setup perform while installing jBulkEmailSender?" & vbCrLf & vbCrLf & _
         "Create a desktop shortcut?"

If MsgBox(strMsg, 4 + 32, strAppTitle) = 6 Then
    strDesktop = objShell.SpecialFolders("Desktop")
    Set objShortCut = objShell.CreateShortcut(strDesktop & "\jBulkEmailSender.lnk")
    
    ' Resolve Target
    strTarget = ""
    If fso.FileExists(strInstallPath & "\jBulkEmailSender.exe") Then
        strTarget = strInstallPath & "\jBulkEmailSender.exe"
    ElseIf fso.FileExists(strInstallPath & "\BulkEmailSender.bat") Then
        strTarget = strInstallPath & "\BulkEmailSender.bat"
    End If
    
    If strTarget <> "" Then
        objShortCut.TargetPath = strTarget
        objShortCut.WorkingDirectory = strInstallPath
        If fso.FileExists(strInstallPath & "\assets\mission_icon.ico") Then
            objShortCut.IconLocation = strInstallPath & "\assets\mission_icon.ico"
        End If
        objShortCut.Save
        strLog = strLog & "  [Shortcut] Desktop Icon -> Created" & vbCrLf
    End If
End If

' --- STEP 6: FINISH SCREEN ---
strFinish = "Completing the jBES Discovery Setup Wizard" & vbCrLf & vbCrLf & _
            "Setup has finished installing jBulkEmailSender on your computer." & vbCrLf & vbCrLf & _
            "Deployment Details:" & vbCrLf & strLog & vbCrLf & _
            "Would you like to launch the application now?"

res = MsgBox(strFinish, 4 + 64, strAppTitle)
If res = 6 Then
    ' Launch based on target
    strLaunch = ""
    If fso.FileExists(strInstallPath & "\jBulkEmailSender.exe") Then
        strLaunch = Chr(34) & strInstallPath & "\jBulkEmailSender.exe" & Chr(34)
    ElseIf fso.FileExists(strInstallPath & "\BulkEmailSender.bat") Then
        strLaunch = Chr(34) & strInstallPath & "\BulkEmailSender.bat" & Chr(34)
    End If
    
    If strLaunch <> "" Then objShell.Run strLaunch
End If
