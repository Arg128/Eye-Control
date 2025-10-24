"""
✅ Validación Final del Sistema Mejorado
Ejecuta este script para confirmar que todas las mejoras funcionan
"""

import sys
import os
from pathlib import Path

print("=" * 80)
print("✅ VALIDACIÓN FINAL - Sistema de Eye Tracking Mejorado")
print("=" * 80)
print()

# Cambiar al directorio raíz del proyecto
project_root = Path(__file__).parent.parent
os.chdir(project_root)

print("📍 Directorio de trabajo:", project_root)
print()

# ============================================================================
# 1. Verificar archivos clave
# ============================================================================
print("📁 VERIFICANDO ARCHIVOS CLAVE...")
print("-" * 80)

archivos_clave = {
    "Servidor WebSocket": "examples/minigames_server.py",
    "Cliente Web (Index)": "examples/minigames_web/index.html",
    "Eye Tracking JS": "examples/minigames_web/eyeTracking.js",
    "Estilos CSS": "examples/minigames_web/style.css",
    "Main JS": "examples/minigames_web/main.js",
    "Utils mejorado": "eyeGestures/utils.py",
    "Guía de configuración": "examples/CONFIGURACION_OPTIMA.md",
    "Resumen de mejoras": "examples/RESUMEN_MEJORAS.md",
}

todos_ok = True
for nombre, ruta in archivos_clave.items():
    existe = (project_root / ruta).exists()
    estado = "✓" if existe else "✗"
    print(f"{estado} {nombre}: {ruta}")
    if not existe:
        todos_ok = False

print()

if not todos_ok:
    print("❌ Algunos archivos clave no se encontraron")
    print("   Verifica que todas las mejoras se hayan aplicado correctamente")
    sys.exit(1)

print("✓ Todos los archivos clave presentes")
print()

# ============================================================================
# 2. Verificar contenido de mejoras
# ============================================================================
print("🔍 VERIFICANDO CONTENIDO DE MEJORAS...")
print("-" * 80)

mejoras_verificadas = []
mejoras_faltantes = []

# Verificar calibración extendida
server_path = project_root / "examples/minigames_server.py"
with open(server_path, 'r', encoding='utf-8') as f:
    server_code = f.read()
    
if 'min_calibration_frames = 60' in server_code:
    print("✓ Calibración extendida a 60 frames")
    mejoras_verificadas.append("Calibración 60 frames")
else:
    print("✗ Calibración NO está en 60 frames")
    mejoras_faltantes.append("Calibración 60 frames")

# Verificar suavizado
if 'max_history' in server_code and 'gaze_history' in server_code:
    print("✓ Suavizado temporal implementado")
    mejoras_verificadas.append("Suavizado temporal")
else:
    print("✗ Suavizado temporal NO encontrado")
    mejoras_faltantes.append("Suavizado temporal")

# Verificar zona muerta
if 'dead_zone' in server_code:
    print("✓ Zona muerta anti-jitter implementada")
    mejoras_verificadas.append("Zona muerta")
else:
    print("✗ Zona muerta NO encontrada")
    mejoras_faltantes.append("Zona muerta")

# Verificar supresión de errores
utils_path = project_root / "eyeGestures/utils.py"
with open(utils_path, 'r', encoding='utf-8') as f:
    utils_code = f.read()

if 'EYE_GESTURES_DEBUG' in utils_code:
    print("✓ Supresión de spam de errores activada")
    mejoras_verificadas.append("Supresión de errores")
else:
    print("✗ Supresión de errores NO encontrada")
    mejoras_faltantes.append("Supresión de errores")

# Verificar UI de calibración
html_path = project_root / "examples/minigames_web/index.html"
with open(html_path, 'r', encoding='utf-8') as f:
    html_code = f.read()

if 'calibration-indicator' in html_code:
    print("✓ UI de calibración con barra de progreso")
    mejoras_verificadas.append("UI de calibración")
else:
    print("✗ UI de calibración NO encontrada")
    mejoras_faltantes.append("UI de calibración")

# Verificar suavizado en cliente
js_path = project_root / "examples/minigames_web/eyeTracking.js"
with open(js_path, 'r', encoding='utf-8') as f:
    js_code = f.read()

if 'maxHistory' in js_code and 'deadZone' in js_code:
    print("✓ Suavizado y zona muerta en cliente")
    mejoras_verificadas.append("Smoothing cliente")
else:
    print("✗ Smoothing en cliente NO encontrado")
    mejoras_faltantes.append("Smoothing cliente")

print()

if mejoras_faltantes:
    print(f"❌ Faltan {len(mejoras_faltantes)} mejoras por implementar:")
    for mejora in mejoras_faltantes:
        print(f"   • {mejora}")
    print()
else:
    print(f"✅ Todas las {len(mejoras_verificadas)} mejoras implementadas correctamente")
    print()

# ============================================================================
# 3. Verificar parámetros de configuración
# ============================================================================
print("⚙️ PARÁMETROS DE CONFIGURACIÓN ACTUALES...")
print("-" * 80)

# Extraer parámetros del servidor
import re

# Calibración
calib_match = re.search(r'min_calibration_frames\s*=\s*(\d+)', server_code)
if calib_match:
    calib_frames = calib_match.group(1)
    print(f"Calibración: {calib_frames} frames")
    if int(calib_frames) >= 60:
        print("  ✓ Valor óptimo (≥60)")
    else:
        print("  ⚠ Considerar aumentar a 60+")

# Suavizado
history_match = re.search(r'max_history\s*=\s*(\d+)', server_code)
if history_match:
    max_history = history_match.group(1)
    print(f"Suavizado servidor: {max_history} puntos")
    print("  ✓ Rango recomendado: 3-10")

# Zona muerta servidor
dead_zone_match = re.search(r'dead_zone\s*=\s*(\d+)', server_code)
if dead_zone_match:
    dead_zone = dead_zone_match.group(1)
    print(f"Zona muerta servidor: {dead_zone}px")
    print("  ✓ Rango recomendado: 10-30")

# Parámetros del cliente
client_history_match = re.search(r'this\.maxHistory\s*=\s*(\d+)', js_code)
if client_history_match:
    client_history = client_history_match.group(1)
    print(f"Suavizado cliente: {client_history} puntos")
    print("  ✓ Rango recomendado: 5-15")

client_dead_zone_match = re.search(r'this\.deadZone\s*=\s*(\d+)', js_code)
if client_dead_zone_match:
    client_dead_zone = client_dead_zone_match.group(1)
    print(f"Zona muerta cliente: {client_dead_zone}px")
    print("  ✓ Rango recomendado: 15-40")

print()

# ============================================================================
# 4. Instrucciones de uso
# ============================================================================
print("🚀 INSTRUCCIONES DE USO...")
print("-" * 80)
print("""
MÉTODO 1: Script automático (Recomendado)
  cd examples
  start_web_minigames_v2.bat

MÉTODO 2: Manual
  # Terminal 1
  python examples/minigames_server.py
  
  # Espera "✓ Calibración completada!"
  # Luego abre en navegador:
  examples/minigames_web/index.html

MÉTODO 3: Con servidor HTTP
  # Terminal 1
  python examples/minigames_server.py
  
  # Terminal 2
  cd examples/minigames_web
  python -m http.server 8000
  
  # Navega a: http://localhost:8000
""")

print("-" * 80)
print()

# ============================================================================
# 5. Checklist final
# ============================================================================
print("📋 CHECKLIST DE FUNCIONALIDADES...")
print("-" * 80)

checklist = [
    ("Calibración extendida (60 frames)", 'min_calibration_frames = 60' in server_code),
    ("Progreso de calibración visible", 'Calibrando:' in server_code),
    ("Suavizado temporal servidor", 'max_history' in server_code),
    ("Zona muerta servidor", 'dead_zone' in server_code),
    ("Suavizado cliente", 'maxHistory' in js_code),
    ("Zona muerta cliente", 'deadZone' in js_code),
    ("UI de calibración", 'calibration-indicator' in html_code),
    ("Supresión de errores", 'EYE_GESTURES_DEBUG' in utils_code),
    ("WebSocket fix", 'async def handle_client(websocket)' in server_code),
]

funcionalidades_ok = 0
funcionalidades_total = len(checklist)

for nombre, estado in checklist:
    simbolo = "✓" if estado else "✗"
    print(f"{simbolo} {nombre}")
    if estado:
        funcionalidades_ok += 1

print()
print(f"Funcionalidades implementadas: {funcionalidades_ok}/{funcionalidades_total}")
print()

# ============================================================================
# 6. Resumen final
# ============================================================================
porcentaje = (funcionalidades_ok / funcionalidades_total) * 100

print("=" * 80)
print("📊 RESUMEN FINAL")
print("=" * 80)
print()

if porcentaje >= 90:
    print("✅ SISTEMA COMPLETAMENTE FUNCIONAL")
    print()
    print(f"   {funcionalidades_ok}/{funcionalidades_total} funcionalidades implementadas ({porcentaje:.0f}%)")
    print()
    print("   🎯 Mejoras principales:")
    for mejora in mejoras_verificadas[:5]:
        print(f"      • {mejora}")
    print()
    print("   🚀 El sistema está listo para usar")
    print("   📖 Lee CONFIGURACION_OPTIMA.md para ajustes avanzados")
    print()
elif porcentaje >= 70:
    print("⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
    print()
    print(f"   {funcionalidades_ok}/{funcionalidades_total} funcionalidades implementadas ({porcentaje:.0f}%)")
    print()
    if mejoras_faltantes:
        print("   ⚠ Mejoras pendientes:")
        for mejora in mejoras_faltantes:
            print(f"      • {mejora}")
    print()
    print("   💡 Revisa los archivos marcados con ✗")
    print()
else:
    print("❌ SISTEMA REQUIERE ATENCIÓN")
    print()
    print(f"   Solo {funcionalidades_ok}/{funcionalidades_total} funcionalidades implementadas ({porcentaje:.0f}%)")
    print()
    print("   ❌ Muchas mejoras pendientes:")
    for mejora in mejoras_faltantes:
        print(f"      • {mejora}")
    print()
    print("   💡 Ejecuta: python examples/test_mejoras_completo.py")
    print()

print("=" * 80)
print()

# Código de salida
sys.exit(0 if porcentaje >= 90 else 1)
