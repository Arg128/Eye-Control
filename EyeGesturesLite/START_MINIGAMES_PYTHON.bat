@echo off
echo ========================================
echo  EyeGestures Minigames - Python Server
echo ========================================
echo.
echo Iniciando servidor HTTP con Python en puerto 8000...
echo.

REM Verificar si Python está disponible
python --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python no esta instalado.
    echo Por favor instala Python desde: https://www.python.org/
    pause
    exit /b 1
)

echo La pagina estara disponible en:
echo http://localhost:8000/minigames/launcher.html
echo.
echo Abre esa URL en tu navegador.
echo.
echo Para detener el servidor, presiona Ctrl+C
echo ========================================
echo.

start http://localhost:8000/minigames/launcher.html

python -m http.server 8000

pause
