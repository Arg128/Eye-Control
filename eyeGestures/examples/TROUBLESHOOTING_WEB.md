# 🔧 Guía de Solución de Problemas - EyeGestures Web Minigames

## ❓ Problema: La página web no se conecta a la cámara

### Síntomas:
- El indicador muestra "Desconectado (usando ratón)"
- El cursor de mirada no responde al movimiento de los ojos
- Solo funciona con el mouse

### Solución Paso a Paso:

#### ✅ Paso 1: Verificar que el servidor está corriendo

**Primero, inicia el servidor:**
```bash
python examples/minigames_server.py
```

**Deberías ver este output:**
```
============================================================
EyeGestures WebSocket Server
============================================================

Initializing eye tracking system...
Eye tracking initialized successfully!
✓ Eye tracking initialized
Screen resolution: 1920x1080

✓ Server starting on ws://localhost:8765
Waiting for web page connections...

Press Ctrl+C to stop the server
```

**Si ves errores aquí:**
- ❌ "Failed to read frame from camera" → Tu cámara no está disponible (ver Paso 2)
- ❌ "ModuleNotFoundError" → Faltan dependencias (ver Paso 3)

#### ✅ Paso 2: Verificar la cámara

**Ejecuta el script de diagnóstico:**
```bash
python examples/troubleshooting_camera.py
```

**Problemas comunes:**
- La cámara está siendo usada por otra aplicación (Zoom, Teams, etc.)
- Permisos de cámara no otorgados
- Driver de cámara desactualizado

**Solución:**
- Cierra todas las aplicaciones que puedan usar la cámara
- Verifica permisos en Configuración de Windows → Privacidad → Cámara

#### ✅ Paso 3: Verificar dependencias

**Instala todas las dependencias necesarias:**
```bash
pip install opencv-python mediapipe numpy websockets
```

#### ✅ Paso 4: Probar la conexión WebSocket

**Ejecuta el test de conexión:**
```bash
python examples/test_connection.py
```

**Deberías ver:**
```
Testing connection to ws://localhost:8765...
✓ Connected successfully!
Receiving data for 10 seconds...

Message #10: x=856, y=432, fixation=0.23
Message #20: x=892, y=445, fixation=0.67
...
```

**Si ves "Connection refused":**
- El servidor no está corriendo → Ve al Paso 1

#### ✅ Paso 5: Abrir la página web DESPUÉS del servidor

**IMPORTANTE: El servidor debe estar corriendo PRIMERO**

1. Inicia el servidor (ver Paso 1)
2. Espera a ver "Waiting for web page connections..."
3. Abre `examples/minigames_web/index.html` en tu navegador

**En la consola del navegador (F12) deberías ver:**
```
Attempting to connect to ws://localhost:8765...
✓ Connected to eye tracking server!
```

#### ✅ Paso 6: Verificar que el servidor recibe la conexión

**En la terminal del servidor deberías ver:**
```
✓ Client connected from ('127.0.0.1', 51234). Total clients: 1
[TRACKING] Gaze: (856, 432) | Fixation: 0.67 | Clients: 1
```

El contador de "Clients: 1" confirma que la página está conectada.

---

## 🎯 Flujo Correcto de Inicio

### Orden correcto:

1. **Terminal 1: Inicia el servidor**
   ```bash
   python examples/minigames_server.py
   ```
   Espera a ver: `Waiting for web page connections...`

2. **Navegador: Abre la página**
   ```
   examples/minigames_web/index.html
   ```

3. **Verificar conexión:**
   - Indicador verde "Conectado"
   - Cursor de mirada moviéndose
   - Números de posición X/Y actualizándose

---

## 📊 Diagnóstico Visual

### Estado del Indicador:

| Color | Estado | Significado |
|-------|--------|-------------|
| 🟢 Verde | Conectado | ✅ Todo funciona correctamente |
| 🔴 Rojo | Desconectado (usando ratón) | ❌ Servidor no disponible |
| ⚪ Blanco | Conectando... | ⏳ Intentando conectar |

### Consola del Navegador (F12):

**✅ Conexión exitosa:**
```javascript
Attempting to connect to ws://localhost:8765...
✓ Connected to eye tracking server!
```

**❌ Sin conexión:**
```javascript
WebSocket error: [Error details]
Switching to mouse fallback mode
```

---

## 🚨 Problemas Comunes

### Problema: "Calibrating: X/25" se queda atascado

**Causa:** El servidor está calibrando pero no detecta tu cara/ojos.

**Solución:**
1. Asegúrate de estar frente a la cámara
2. Buena iluminación en tu rostro
3. Mira directamente a la cámara durante los primeros segundos

### Problema: El cursor salta o es impreciso

**Causa:** Mala calibración o iluminación.

**Solución:**
1. Reinicia el servidor para recalibrar
2. Mejora la iluminación
3. Limpia la lente de tu cámara
4. Mantén tu cabeza más estable

### Problema: El navegador bloquea WebSocket

**Causa:** Algunos navegadores/antivirus bloquean conexiones locales.

**Solución:**
1. Usa Chrome o Firefox (recomendado)
2. Desactiva temporalmente extensiones de seguridad
3. Agrega localhost:8765 a excepciones del firewall

---

## 🔍 Logs y Debug

### Ver logs del servidor:
El servidor imprime información útil cada 10 frames:
```
[TRACKING] Gaze: (856, 432) | Fixation: 0.67 | Clients: 1
```

- **CALIBRATING**: Primeros 25 frames
- **TRACKING**: Después de calibración
- **Gaze**: Posición actual del cursor
- **Fixation**: Nivel de fijación (0-1)
- **Clients**: Número de páginas web conectadas

### Ver logs del navegador:
Abre la consola (F12) y busca mensajes de eye-tracking.

---

## 📞 Necesitas más ayuda?

Si sigues teniendo problemas después de seguir estos pasos:

1. Abre un issue en GitHub con:
   - Output completo del servidor
   - Logs de la consola del navegador
   - Tu sistema operativo y versión de Python
   - Especificaciones de tu cámara

2. Prueba el modo de respaldo (ratón) mientras tanto:
   - Los juegos funcionarán con el mouse automáticamente
   - Útil para probar la funcionalidad sin eye-tracking

---

## ✅ Checklist de Verificación

Antes de reportar un problema, verifica:

- [ ] Python 3.7+ instalado
- [ ] Todas las dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Cámara funcionando (probar con otra app)
- [ ] Servidor iniciado y mostrando "Waiting for connections..."
- [ ] Página abierta DESPUÉS de iniciar el servidor
- [ ] Puerto 8765 no bloqueado por firewall
- [ ] Navegador moderno (Chrome/Firefox/Edge)
- [ ] Consola del navegador abierta (F12) para ver logs

---

**¡Feliz gaming con eye-tracking! 🎮👁️**
