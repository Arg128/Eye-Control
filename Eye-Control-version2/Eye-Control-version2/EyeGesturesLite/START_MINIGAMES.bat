@echo off
echo ========================================
echo  EyeGestures Minigames - Servidor Local
echo ========================================
echo.
echo Iniciando servidor HTTP en puerto 8000...
echo.

REM Verificar si http-server está disponible
where npx >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js no esta instalado.
    echo Por favor instala Node.js desde: https://nodejs.org/
    pause
    exit /b 1
)

echo Abriendo navegador...
echo.
echo La pagina se abrira automaticamente en:
echo http://localhost:8000/minigames/launcher.html
echo.
echo Para detener el servidor, presiona Ctrl+C
echo ========================================
echo.

npx http-server -p 8000 -o /minigames/launcher.html

pause
