@echo off
chcp 65001
cls
echo 影刀数据表格清洗工具
echo ======================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查文件是否存在
if not exist "影刀数据表格_20250916-143820.xlsx" (
    echo 文件 "影刀数据表格_20250916-143820.xlsx" 未找到
    echo 请将文件放在当前目录
    pause
    exit /b 1
)

echo 正在处理数据...
python excel_cleaner_simple.py

echo.
echo 处理完成！
echo 请查看生成的文件：
echo - 影刀数据表格_20250916-143820_清洗后.csv
echo - 影刀数据表格_20250916-143820_清洗后.json  
echo - 影刀数据表格_20250916-143820_清洗后.txt
echo - 影刀数据表格_20250916-143820_清洗报告.txt
echo.
pause