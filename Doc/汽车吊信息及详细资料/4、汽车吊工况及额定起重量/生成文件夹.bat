@echo off
setlocal enabledelayedexpansion

REM �����ļ�·��������txt�ļ���bat�ű���ͬһĿ¼��
set "inputFile=��������ź�����.txt"


REM ����ļ��Ƿ����
if not exist "%inputFile%" (
    echo δ�ҵ��ļ� %inputFile%
    pause
    exit /b
)

REM ���ж�ȡ�ļ��������ļ���
for /f "usebackq tokens=1,2 delims=	" %%A in ("%inputFile%") do (
    set "folderName=%%A-%%B"
    mkdir "!folderName!" >nul 2>nul
)

echo �ļ��д�����ɡ�
pause
