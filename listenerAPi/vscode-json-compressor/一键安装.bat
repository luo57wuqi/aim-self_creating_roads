@echo off
echo 正在安装文本格式化插件...
echo.
echo 方法1：直接复制到扩展目录
echo.

REM 获取用户目录
set "userDir=%USERPROFILE%"
set "extDir=%userDir%\.vscode\extensions\text-formatter"

REM 创建扩展目录
mkdir "%extDir%" 2>nul

REM 复制文件
copy extension.js "%extDir%\extension.js" >nul
copy package.json "%extDir%\package.json" >nul
copy README.md "%extDir%\README.md" >nul

echo 文件已复制到扩展目录：
echo %extDir%
echo.
echo 安装完成！请重启TraeIDE/VS Code
echo.
echo 使用方法：
echo 1. 打开任意文本文件
echo 2. 选中文本
echo 3. 按 Alt+L 格式化
echo 4. 再按 Alt+L 恢复原始格式
pause