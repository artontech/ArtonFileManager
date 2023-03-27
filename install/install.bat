@ECHO OFF
SET MIRROR=-i https://pypi.tuna.tsinghua.edu.cn/simple/
cd /d %~dp0
pip install --upgrade pip wheel
pip install -r requirements.txt %MIRROR%
pause