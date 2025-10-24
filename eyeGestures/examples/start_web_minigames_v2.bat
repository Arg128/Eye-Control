@echo off
REM Script de inicio mejorado con verificacion completa
SETLOCAL EnableDelayedExpansion

echo ============================================================
echo    EyeGestures - Iniciador con Verificacion
echo ============================================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar que python este disponible
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Verificando Python...
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
echo   %PYTHON_VER%

echo.
echo [2/5] Verificando dependencias...
python -c "import cv2, numpy, websockets, mediapipe" 2>nul
if errorlevel 1 (
    echo   Algunas dependencias faltan. Instalando...
    echo.
    python -m pip install opencv-python numpy websockets mediapipe pygame
    if errorlevel 1 (
        echo.
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
    echo   Dependencias instaladas correctamente
) else (
    echo   Todas las dependencias instaladas
)

echo.
echo [3/5] Verificando camara...
python -c "import cv2; cap = cv2.VideoCapture(0); ret, _ = cap.read(); cap.release(); exit(0 if ret else 1)" 2>nul
if errorlevel 1 (
    echo   ADVERTENCIA: No se pudo acceder a la camara
    echo.
    echo   Posibles causas:
    echo   - Camara no conectada
    echo   - Otra aplicacion esta usando la camara
    echo   - Permisos de camara no otorgados
    echo.
    echo   El servidor intentara iniciarse de todas formas...
    timeout /t 3 >nul
) else (
    echo   Camara accesible
)

echo.
echo [4/5] Preparando servidor WebSocket...
echo   Puerto: 8765
echo   Host: localhost

echo.
echo [5/5] Iniciando...
echo.
echo ============================================================
echo   INSTRUCCIONES:
echo ============================================================
echo   1. El servidor se iniciara en esta ventana
echo   2. En 3 segundos se abrira la pagina web automaticamente
echo   3. Verifica que el indicador este en VERDE "Conectado"
echo   4. Para detener el servidor: Ctrl+C
echo ============================================================
echo.

REM Abrir la pagina web con retraso
start "" cmd /c "timeout /t 3 >nul && start minigames_web\index.html && echo Pagina web abierta..."

echo Iniciando servidor...
echo.
python minigames_server.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo   ERROR AL EJECUTAR EL SERVIDOR
    echo ============================================================
    echo.
    echo   Si el problema persiste:
    echo   1. Ejecuta: python diagnostico_completo.py
    echo   2. Lee: TROUBLESHOOTING_WEB.md
    echo   3. Verifica que la camara funcione con otra app
    echo.
)

echo.
echo Servidor detenido.
pause
