# 🚨 SOLUCIÓN RÁPIDA - Problemas Comunes

## ⚡ PROBLEMA: FPS muy bajos en juegos nativos

### Causas:
1. ❌ No hay calibración previa
2. ❌ Procesamiento de video muy pesado
3. ❌ Detección facial fallando constantemente

### ✅ SOLUCIÓN:
```bash
# Ejecuta el juego nativo (ahora con calibración automática)
python examples/minigames_pygame.py
```

**Mejoras implementadas:**
- ✅ Calibración automática al inicio (50 frames)
- ✅ Pantalla de progreso de calibración
- ✅ Mejor manejo de frames sin detección
- ✅ Indicador visual de FPS
- ✅ Advertencia cuando no se detectan ojos

---

## 👁️ PROBLEMA: No reconoce los ojos

### Síntomas:
- "No se detectan ojos" en pantalla
- Cursor de mirada no aparece
- FPS muy bajos

### ✅ SOLUCIONES:

#### 1. Ejecuta el diagnóstico:
```bash
python examples/diagnostico_completo.py
```

#### 2. Verifica tu cámara:
```bash
python examples/troubleshooting_camera.py
```

#### 3. Mejora las condiciones:
- ✅ **Iluminación**: Enciende luces, mira hacia una ventana
- ✅ **Distancia**: 50-70cm de la cámara
- ✅ **Posición**: Rostro centrado frente a la cámara
- ✅ **Limpieza**: Limpia la lente de tu cámara
- ✅ **Ángulo**: La cámara debe estar a la altura de tus ojos

#### 4. Verifica que no haya conflictos:
- ✅ Cierra Zoom, Teams, Skype
- ✅ Cierra otras apps que usen la cámara
- ✅ Reinicia tu computadora si es necesario

---

## 🌐 PROBLEMA: Página web desconectada

### Síntomas:
- Indicador rojo "Desconectado (usando ratón)"
- Solo funciona con el mouse
- No hay cursor de mirada

### ✅ SOLUCIÓN PASO A PASO:

#### Paso 1: Inicia el servidor PRIMERO
```bash
python examples/minigames_server.py
```

**Deberías ver:**
```
============================================================
   EyeGestures WebSocket Server v2.0
============================================================

→ Inicializando EyeGestures_v2...
  ✓ EyeGestures_v2 inicializado
→ Conectando con cámara...
  ✓ Cámara conectada (resolución: 640x480)
→ Configurando calibración...
  ✓ Calibración configurada

✓ Eye tracking inicializado correctamente!

============================================================
✓ Servidor WebSocket iniciado en ws://localhost:8765
============================================================
```

#### Paso 2: Espera 3 segundos
- El servidor necesita calibrarse automáticamente
- Verás mensajes como: `[CALIBRATING] ...`

#### Paso 3: Abre la página web
```
examples/minigames_web/index.html
```

#### Paso 4: Verifica la conexión
- **En el navegador (F12 → Console):**
  ```javascript
  Attempting to connect to ws://localhost:8765...
  ✓ Connected to eye tracking server!
  ```

- **En el servidor:**
  ```
  ✓ Client connected from ('127.0.0.1', 51234). Total clients: 1
  [TRACKING] Gaze: (856, 432) | Fixation: 0.67 | Clients: 1
  ```

---

## 🎮 USO SIMPLIFICADO

### Opción 1: Script automático (Windows)
```bash
cd examples
start_web_minigames_v2.bat
```
Este script hace TODO automáticamente:
- ✅ Verifica dependencias
- ✅ Instala lo que falta
- ✅ Verifica la cámara
- ✅ Inicia el servidor
- ✅ Abre la página web

### Opción 2: Launcher
```bash
python examples/launcher.py
```
- Selecciona "Web Minigames"
- Todo se configura automáticamente

### Opción 3: Diagnóstico completo
```bash
python examples/diagnostico_completo.py
```
- Verifica TODO el sistema
- Te dice exactamente qué falta o está mal

---

## 📊 VERIFICACIÓN RÁPIDA

### ✅ Checklist antes de jugar:

**Sistema:**
- [ ] Python 3.7+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)

**Cámara:**
- [ ] Cámara conectada y encendida
- [ ] No usada por otras apps
- [ ] Luz de la cámara encendida

**Para juegos nativos (pygame):**
- [ ] Ejecutar: `python examples/minigames_pygame.py`
- [ ] Esperar pantalla de calibración (3 segundos)
- [ ] FPS > 30 (mostrado en pantalla)
- [ ] Ver cursor de mirada moviéndose

**Para juegos web:**
- [ ] Servidor corriendo primero
- [ ] Ver "✓ Servidor WebSocket iniciado..."
- [ ] Esperar 3 segundos para calibración
- [ ] Abrir página web después
- [ ] Indicador verde "Conectado"
- [ ] Números X/Y actualizándose

---

## 🔧 COMANDOS DE DIAGNÓSTICO

### 1. Test completo del sistema:
```bash
python examples/diagnostico_completo.py
```

### 2. Test de cámara:
```bash
python examples/troubleshooting_camera.py
```

### 3. Test de conexión WebSocket:
```bash
python examples/test_connection.py
```

### 4. Ver qué puerto está usando:
```bash
netstat -an | find "8765"
```

---

## 🆘 SI NADA FUNCIONA

### 1. Reinstala dependencias:
```bash
pip uninstall opencv-python mediapipe numpy
pip install opencv-python mediapipe numpy
```

### 2. Verifica permisos de cámara:
**Windows:**
- Configuración → Privacidad → Cámara
- Activar "Permitir que las aplicaciones accedan a la cámara"

### 3. Prueba con otra cámara:
Si tienes cámara externa USB, prueba con ella.

### 4. Modo de respaldo (solo para probar):
La página web funciona con el mouse automáticamente si no hay servidor.
Esto te permite probar los juegos mientras resuelves el problema del eye-tracking.

---

## 📝 RESUMEN DE MEJORAS IMPLEMENTADAS

### Juegos Nativos (minigames_pygame.py):
- ✅ Calibración automática al inicio con pantalla de progreso
- ✅ Mejor detección y manejo de errores
- ✅ Indicador visual de FPS en tiempo real
- ✅ Advertencia cuando no se detectan ojos
- ✅ Pantalla de error informativa
- ✅ Mejor feedback visual del cursor de mirada

### Servidor Web (minigames_server.py):
- ✅ Inicialización robusta con manejo de errores
- ✅ Verificación de cámara antes de iniciar
- ✅ Mensajes informativos paso a paso
- ✅ Mejor logging de conexiones y estado
- ✅ Instrucciones claras en consola

### Scripts de Ayuda:
- ✅ `diagnostico_completo.py` - Verifica todo el sistema
- ✅ `start_web_minigames_v2.bat` - Inicio automático mejorado
- ✅ Documentación actualizada

---

## 🎯 INICIO RÁPIDO RECOMENDADO

```bash
# 1. Diagnóstico (opcional pero recomendado)
python examples/diagnostico_completo.py

# 2. Para juegos nativos:
python examples/minigames_pygame.py

# 3. Para juegos web:
cd examples
start_web_minigames_v2.bat
```

**¡Ahora todo debería funcionar correctamente! 🎮👁️**
