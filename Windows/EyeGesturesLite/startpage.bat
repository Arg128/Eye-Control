@echo off
:: ============================================
:: EyeGestures Hub - Iniciador Rápido
:: ============================================

title EyeGestures Hub - Iniciando...

echo.
echo  ========================================
echo     _____ _   _ _____  
echo    ^|_   _^| ^| ^| ^|  ___^| 
echo      ^| ^| ^| ^|_^| ^| ^|__   
echo      ^| ^| ^|  _  ^|  __^|  
echo     _^| ^|_^| ^| ^| ^| ^|___  
echo     \___/\_^| ^|_/\____/  
echo.
echo     EyeGestures Hub v2.0
echo  ========================================
echo.

:: Verificar si Node.js está instalado
echo [1/4] Verificando Node.js...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo  [X] ERROR: Node.js no esta instalado
    echo.
    echo  Por favor, instala Node.js desde:
    echo  https://nodejs.org/
    echo.
    pause
    exit /b 1
)

node --version
echo  [OK] Node.js encontrado
echo.

:: Instalar/verificar http-server usando npx (no requiere instalación global)
echo [2/4] Preparando http-server...
echo  [OK] http-server listo (usando npx)
echo.

:: Verificar puerto disponible
echo [3/4] Verificando puerto 8000...
netstat -ano | findstr ":8000" >nul 2>nul
if %errorlevel% equ 0 (
    echo  [!] Puerto 8000 en uso
    echo  [+] Intentando detener proceso...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
        taskkill /F /PID %%a >nul 2>nul
    )
    timeout /t 2 >nul
)

echo  [OK] Puerto disponible
echo.

:: Iniciar servidor
echo [4/4] Iniciando servidor...
echo.
echo  ========================================
echo   Servidor HTTP iniciado correctamente
echo  ========================================
echo.
echo   URL Local:    http://localhost:8000/minigames/hub.html
echo   URL Red:      http://127.0.0.1:8000/minigames/hub.html
echo.
echo   Presiona Ctrl+C para detener el servidor
echo  ========================================
echo.

:: Esperar 2 segundos y abrir navegador
timeout /t 2 >nul
start http://localhost:8000/minigames/hub.html

:: Iniciar http-server usando npx (descarga automática si no existe)
cd /d "%~dp0"
npx http-server -p 8000 -c-1

:: Si el servidor se detiene
echo.
echo  [!] Servidor detenido
pause
