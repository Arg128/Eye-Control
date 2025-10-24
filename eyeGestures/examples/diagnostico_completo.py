"""
Script de Diagnóstico Completo para EyeGestures
Verifica todos los componentes del sistema
"""

import sys
import os

print("="*70)
print("   DIAGNÓSTICO COMPLETO - EyeGestures")
print("="*70)
print()

# 1. Check Python version
print("1. Verificando versión de Python...")
print(f"   Python {sys.version}")
if sys.version_info < (3, 7):
    print("   ✗ ADVERTENCIA: Se recomienda Python 3.7 o superior")
else:
    print("   ✓ Versión de Python adecuada")
print()

# 2. Check dependencies
print("2. Verificando dependencias instaladas...")
dependencies = {
    'cv2': 'opencv-python',
    'numpy': 'numpy',
    'pygame': 'pygame',
    'websockets': 'websockets',
    'mediapipe': 'mediapipe'
}

missing_deps = []
for module, package in dependencies.items():
    try:
        __import__(module)
        if module == 'cv2':
            import cv2
            print(f"   ✓ {package} (versión {cv2.__version__})")
        elif module == 'numpy':
            import numpy as np
            print(f"   ✓ {package} (versión {np.__version__})")
        elif module == 'pygame':
            import pygame
            print(f"   ✓ {package} (versión {pygame.version.ver})")
        elif module == 'websockets':
            import websockets
            print(f"   ✓ {package} (versión {websockets.__version__})")
        elif module == 'mediapipe':
            import mediapipe as mp
            print(f"   ✓ {package} (versión {mp.__version__})")
    except ImportError:
        print(f"   ✗ {package} NO INSTALADO")
        missing_deps.append(package)

if missing_deps:
    print()
    print("   Instala las dependencias faltantes con:")
    print(f"   pip install {' '.join(missing_deps)}")
    print()
else:
    print("   ✓ Todas las dependencias instaladas")
print()

# 3. Check camera
print("3. Verificando acceso a la cámara...")
try:
    import cv2
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("   ✗ No se pudo abrir la cámara")
        print("   Posibles causas:")
        print("     - Cámara no conectada")
        print("     - Otra aplicación está usando la cámara")
        print("     - Permisos de cámara no otorgados")
    else:
        ret, frame = cap.read()
        if ret:
            height, width = frame.shape[:2]
            print(f"   ✓ Cámara funcionando (resolución: {width}x{height})")
            
            # Test face detection
            try:
                sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                from eyeGestures import EyeGestures_v2
                
                print("   → Probando detección facial...")
                gestures = EyeGestures_v2()
                
                # Try a few frames
                detected = False
                for i in range(10):
                    ret, frame = cap.read()
                    if ret:
                        import numpy as np
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        event, _ = gestures.step(frame_rgb, False, 1920, 1080, context="test")
                        if event is not None:
                            detected = True
                            print(f"   ✓ Rostro detectado! (Posición: {event.point})")
                            break
                
                if not detected:
                    print("   ⚠ No se detectó ningún rostro")
                    print("   Asegúrate de:")
                    print("     - Estar frente a la cámara")
                    print("     - Tener buena iluminación")
                    print("     - Que tu rostro sea visible")
                    
            except Exception as e:
                print(f"   ✗ Error al probar detección: {e}")
        else:
            print("   ✗ No se pudo leer de la cámara")
        
        cap.release()
except Exception as e:
    print(f"   ✗ Error al acceder a la cámara: {e}")
print()

# 4. Check files
print("4. Verificando archivos del proyecto...")
base_path = os.path.dirname(__file__)
required_files = [
    'launcher.py',
    'minigames_server.py',
    'minigames_pygame.py',
    'minigames_web/index.html',
    'minigames_web/eyeTracking.js',
    'minigames_web/games.js',
    'minigames_web/main.js',
    'minigames_web/style.css'
]

all_files_present = True
for file in required_files:
    file_path = os.path.join(base_path, file)
    if os.path.exists(file_path):
        print(f"   ✓ {file}")
    else:
        print(f"   ✗ {file} NO ENCONTRADO")
        all_files_present = False

if all_files_present:
    print("   ✓ Todos los archivos presentes")
print()

# 5. Check network
print("5. Verificando conectividad de red...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('localhost', 8765))
    sock.close()
    
    if result == 0:
        print("   ⚠ Puerto 8765 ya está en uso")
        print("   Esto podría significar que:")
        print("     - El servidor ya está corriendo")
        print("     - Otra aplicación usa el puerto 8765")
    else:
        print("   ✓ Puerto 8765 disponible")
except Exception as e:
    print(f"   ⚠ No se pudo verificar puerto: {e}")
print()

# 6. Summary
print("="*70)
print("   RESUMEN DEL DIAGNÓSTICO")
print("="*70)

issues = []
if sys.version_info < (3, 7):
    issues.append("⚠ Actualiza Python a versión 3.7+")
if missing_deps:
    issues.append(f"✗ Instala dependencias: {', '.join(missing_deps)}")
if not all_files_present:
    issues.append("✗ Algunos archivos del proyecto faltan")

if issues:
    print("\nProblemas encontrados:")
    for issue in issues:
        print(f"  {issue}")
    print()
    print("Soluciones recomendadas:")
    if missing_deps:
        print(f"  1. pip install {' '.join(missing_deps)}")
    print("  2. Asegúrate de estar en el directorio correcto")
    print("  3. Revisa TROUBLESHOOTING_WEB.md para más ayuda")
else:
    print("\n✓ ¡Sistema listo para usar!")
    print()
    print("Siguiente paso:")
    print("  python launcher.py")
    print()
    print("O para juegos web:")
    print("  1. python minigames_server.py")
    print("  2. Abre minigames_web/index.html")

print()
print("="*70)
print()

# Wait for user
input("Presiona Enter para continuar...")
