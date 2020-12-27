@ECHO OFF
echo get admin permission
cacls.exe "%SystemDrive%\System Volume Information" >nul 2>nul
if %errorlevel%==0 goto Admin
%1 mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit
exit

:Admin
cd /d "%~dp0"
python %~dp0/server.py
pause