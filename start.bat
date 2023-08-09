@ECHO OFF
cd /d %~dp0
start frontend\start.bat
call backend\start.bat
