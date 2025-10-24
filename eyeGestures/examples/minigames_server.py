"""
EyeGestures WebSocket Server
Streams eye tracking data to web applications
"""

import os
import sys
import cv2
import asyncio
import websockets
import json
import numpy as np
import warnings

# Suppress TensorFlow and other warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v2

# Global variables
gestures = None
cap = None
clients = set()
current_data = {"x": 0, "y": 0, "fixation": 0}

def init_eye_tracking():
    """Initialize eye tracking system"""
    global gestures, cap
    
    try:
        print("→ Inicializando EyeGestures_v2...")
        gestures = EyeGestures_v2()
        print("  ✓ EyeGestures_v2 inicializado")
        
        print("→ Conectando con cámara...")
        cap = VideoCapture(0)
        
        # Test camera
        ret, test_frame = cap.read()
        if not ret:
            raise Exception("No se pudo leer de la cámara")
        print(f"  ✓ Cámara conectada (resolución: {test_frame.shape[1]}x{test_frame.shape[0]})")
        
        # Setup calibration
        print("→ Configurando calibración...")
        x = np.arange(0, 1.1, 0.2)
        y = np.arange(0, 1.1, 0.2)
        xx, yy = np.meshgrid(x, y)
        calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
        np.random.shuffle(calibration_map)
        
        gestures.uploadCalibrationMap(calibration_map, context="web_context")
        gestures.setClassicalImpact(2)
        gestures.setFixation(1.0)
        print("  ✓ Calibración configurada")
        
        print("\n✓ Eye tracking inicializado correctamente!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error al inicializar eye tracking: {e}")
        print("\nSoluciones:")
        print("1. Verifica que tu cámara esté conectada y funcionando")
        print("2. Cierra otras aplicaciones que usen la cámara (Zoom, Teams, etc.)")
        print("3. Ejecuta: python troubleshooting_camera.py")
        print("4. Verifica que tengas instalado: pip install opencv-python mediapipe")
        return False

async def send_data():
    """Send eye tracking data to all connected clients"""
    # Get screen dimensions
    import tkinter as tk
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    
    print(f"Screen resolution: {screen_width}x{screen_height}")
    
    # Calibración extendida para mejor precisión
    calibration_counter = 0
    calibrating = True
    frames_without_detection = 0
    
    # Buffer para suavizado de datos
    gaze_history = []
    max_history = 5
    
    # Parámetros de calidad
    min_calibration_frames = 60  # Aumentado de 25 a 60 para mejor calibración
    calibration_quality_threshold = 0.7
    
    print(f"→ Iniciando calibración extendida ({min_calibration_frames} frames)...")
    print("  Mantén tu cabeza estable y mira directamente a la cámara")
    
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(0.1)
                continue
                
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Calibración extendida
            if calibration_counter < min_calibration_frames:
                calibrating = True
                calibration_counter += 1
                
                # Mostrar progreso de calibración
                if calibration_counter % 10 == 0:
                    progress_pct = (calibration_counter / min_calibration_frames) * 100
                    print(f"  Calibrando: {calibration_counter}/{min_calibration_frames} ({progress_pct:.0f}%)")
            else:
                if calibrating:
                    print("  ✓ Calibración completada!")
                    print("→ Modo tracking activado")
                calibrating = False
            
            # Process eye tracking con manejo robusto
            try:
                event, calibration = gestures.step(
                    frame, 
                    calibrating,
                    screen_width, 
                    screen_height, 
                    context="web_context"
                )
                
                if event is not None and hasattr(event, 'point') and hasattr(event, 'fixation'):
                    raw_x = int(event.point[0])
                    raw_y = int(event.point[1])
                    
                    # Aplicar suavizado temporal
                    gaze_history.append({'x': raw_x, 'y': raw_y, 'fixation': float(event.fixation)})
                    if len(gaze_history) > max_history:
                        gaze_history.pop(0)
                    
                    # Promedio ponderado (más peso a datos recientes)
                    if len(gaze_history) > 1:
                        total_weight = 0
                        weighted_x = 0
                        weighted_y = 0
                        weighted_fixation = 0
                        
                        for i, data in enumerate(gaze_history):
                            weight = i + 1  # Peso lineal creciente
                            weighted_x += data['x'] * weight
                            weighted_y += data['y'] * weight
                            weighted_fixation += data['fixation'] * weight
                            total_weight += weight
                        
                        smoothed_x = int(weighted_x / total_weight)
                        smoothed_y = int(weighted_y / total_weight)
                        smoothed_fixation = weighted_fixation / total_weight
                    else:
                        smoothed_x = raw_x
                        smoothed_y = raw_y
                        smoothed_fixation = float(event.fixation)
                    
                    # Aplicar zona muerta para reducir jitter
                    dead_zone = 15  # píxeles
                    if 'last_sent_x' in current_data:
                        dx = abs(smoothed_x - current_data['last_sent_x'])
                        dy = abs(smoothed_y - current_data['last_sent_y'])
                        
                        if dx < dead_zone and dy < dead_zone and not calibrating:
                            # Mantener posición anterior si el movimiento es muy pequeño
                            smoothed_x = current_data['last_sent_x']
                            smoothed_y = current_data['last_sent_y']
                    
                    current_data["x"] = smoothed_x
                    current_data["y"] = smoothed_y
                    current_data["fixation"] = smoothed_fixation
                    current_data["calibrating"] = calibrating
                    current_data["calibration_progress"] = calibration_counter
                    current_data["last_sent_x"] = smoothed_x
                    current_data["last_sent_y"] = smoothed_y
                    current_data["quality"] = 1.0  # Indicador de calidad
                    
                    frames_without_detection = 0
                    
                    # Enviar a todos los clientes
                    if clients:
                        message = json.dumps(current_data)
                        websockets.broadcast(clients, message)
                        
                    # Logging reducido - solo cada 2 segundos en modo tracking
                    if calibrating or (calibration_counter % 120 == 0 and not calibrating):
                        status = "CALIBRANDO" if calibrating else "TRACKING"
                        print(f"[{status}] Gaze: ({current_data['x']}, {current_data['y']}) | "
                              f"Fixation: {current_data['fixation']:.2f} | Clients: {len(clients)}")
                else:
                    frames_without_detection += 1
                    
                    # Alertar solo si no hay detección por mucho tiempo
                    if frames_without_detection == 180:  # 3 segundos
                        print(f"⚠ No se detecta rostro. Verifica iluminación y posición.")
                    elif frames_without_detection % 600 == 0:  # Cada 10 segundos
                        print(f"⚠ Sin detección por {frames_without_detection//60} segundos")
                        
            except AttributeError:
                # Silencioso: normal cuando no hay cara detectada
                frames_without_detection += 1
            except Exception as step_error:
                if frames_without_detection % 120 == 0:
                    print(f"Error en procesamiento: {step_error}")
            
        except Exception as e:
            print(f"Error en bucle principal: {e}")
            import traceback
            traceback.print_exc()
        
        await asyncio.sleep(0.016)  # ~60 FPS

async def handle_client(websocket):
    """Handle individual client connections"""
    clients.add(websocket)
    print(f"✓ Client connected from {websocket.remote_address}. Total clients: {len(clients)}")
    try:
        # Keep connection alive and handle messages
        async for message in websocket:
            # Echo back or handle client messages if needed
            try:
                data = json.loads(message)
                if data.get('type') == 'ping':
                    await websocket.send(json.dumps({'type': 'pong'}))
            except:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"Error in client handler: {e}")
    finally:
        clients.remove(websocket)
        print(f"✗ Client disconnected. Total clients: {len(clients)}")

async def main():
    """Main server function"""
    print("="*60)
    print("   EyeGestures WebSocket Server v2.0")
    print("="*60)
    print()
    
    # Initialize eye tracking
    if not init_eye_tracking():
        print("\n" + "="*60)
        print("ERROR: No se pudo inicializar el sistema")
        print("="*60)
        input("\nPresiona Enter para salir...")
        return
    
    print()
    print("="*60)
    print(f"✓ Servidor WebSocket iniciado en ws://localhost:8765")
    print("="*60)
    print()
    print("Esperando conexiones de páginas web...")
    print()
    print("Instrucciones:")
    print("  1. Abre examples/minigames_web/index.html en tu navegador")
    print("  2. Verifica que aparezca 'Conectado' en verde")
    print("  3. El cursor de mirada debería aparecer en la página")
    print()
    print("Para detener el servidor: Ctrl+C")
    print("="*60)
    print()
    
    try:
        # Start server and data sending concurrently
        async with websockets.serve(handle_client, "localhost", 8765):
            await send_data()
    except KeyboardInterrupt:
        print("\n\nServidor detenido por el usuario")
    except Exception as e:
        print(f"\n\nError en el servidor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cap:
            cap.release()
