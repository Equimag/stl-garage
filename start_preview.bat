@echo off
chcp 65001 > nul
echo ========================================================
echo   STL GARAGE // Запуск локального предпросмотра
echo ========================================================
echo.
echo Открытие сайта по адресу: http://localhost:8080
start http://localhost:8080
python -m http.server 8080
pause
