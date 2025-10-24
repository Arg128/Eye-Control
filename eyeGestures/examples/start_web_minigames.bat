@echo off
REM EyeGestures Web Minigames - Iniciador Completo
REM Este script inicia el servidor y abre automaticamente la pagina web

echo ============================================================
echo   EyeGestures - Web Minigames Launcher
echo ============================================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "minigames_server.py" (
    echo ERROR: Este script debe ejecutarse desde el directorio examples/
    echo.
    pause
    exit /b 1
)

echo [1/3] Verificando dependencias...
D:\github\EyeGestures\venv\Scripts\python.exe -c "import websockets, cv2, numpy" 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Faltan dependencias. Instalando...
    D:\github\EyeGestures\venv\Scripts\python.exe -m pip install websockets opencv-python numpy mediapipe
    echo.
)

echo [2/3] Iniciando servidor de eye-tracking...
echo.
echo IMPORTANTE: 
echo - El servidor se ejecutara en esta ventana
echo - La pagina web se abrira automaticamente
echo - Para detener el servidor, presiona Ctrl+C
echo.
timeout /t 2 >nul

REM Abrir la pagina web con un retraso
start "" cmd /c "timeout /t 3 >nul && start minigames_web\index.html"

echo [3/3] Ejecutando servidor...
echo ============================================================
echo.

REM Iniciar el servidor (esto bloqueara hasta Ctrl+C)
D:\github\EyeGestures\venv\Scripts\python.exe minigames_server.py

echo.
echo Servidor detenido.
pause
