@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Cai/cap nhat thu vien DESKTOP Windows...
python -m pip install -r requirements_desktop.txt
if errorlevel 1 (
  echo.
  echo Khong cai duoc thu vien. Kiem tra Python va Internet.
  pause
  exit /b 1
)
echo.
echo Khoi dong QLDA Xay dung V4.1.0 AI - Desktop mode...
python main.py
if errorlevel 1 (
  echo.
  echo App ket thuc voi loi. Co the kiem tra Microsoft Project COM bang:
  echo     python test_project_com.py
)
pause
