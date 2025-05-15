@echo off
setlocal enabledelayedexpansion

REM 设置文件路径，假设txt文件与bat脚本在同一目录下
set "inputFile=汽车吊编号和类型.txt"


REM 检查文件是否存在
if not exist "%inputFile%" (
    echo 未找到文件 %inputFile%
    pause
    exit /b
)

REM 逐行读取文件并创建文件夹
for /f "usebackq tokens=1,2 delims=	" %%A in ("%inputFile%") do (
    set "folderName=%%A-%%B"
    mkdir "!folderName!" >nul 2>nul
)

echo 文件夹创建完成。
pause
