@echo off
echo ���ڰ�װ JSON Compressor VSCode ���...
echo.

REM ����Ƿ�װ��VSCode
where code >nul 2>nul
if %errorlevel% neq 0 (
    echo ����: δ�ҵ�VSCode�����Ȱ�װVSCode
    pause
    exit /b 1
)

REM ����Ƿ�װ��vsce
where vsce >nul 2>nul
if %errorlevel% neq 0 (
    echo ���ڰ�װvsce����...
    npm install -g vsce
)

echo ���ڴ�����...
cd /d "%~dp0"
vsce package

if %errorlevel% neq 0 (
    echo ���ʧ�ܣ�����ֱ�Ӱ�װ...
    echo ���ֶ���װ��
    echo 1. ��VSCode
    echo 2. �� Ctrl+Shift+P
    echo 3. ���� "Extensions: Install from VSIX"
    echo 4. ѡ�����ɵ� .vsix �ļ�
    pause
    exit /b 1
)

echo ���ڰ�װ���...
for %%f in (*.vsix) do (
    code --install-extension "%%f"
    echo ��� %%f ��װ��ɣ�
    goto :end
)

:end
echo.
echo ��װ��ɣ�������VSCodeʹ�ò��
pause