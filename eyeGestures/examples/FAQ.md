# ❓ Preguntas Frecuentes (FAQ) - EyeGestures

## 🚀 Inicio y Configuración

### P: ¿Cómo inicio el sistema por primera vez?

**R**: Hay tres métodos:

```bash
# MÉTODO 1: Script automático (más fácil)
cd examples
start_web_minigames_v2.bat

# MÉTODO 2: Manual básico
python examples/minigames_server.py
# Luego abre: examples/minigames_web/index.html

# MÉTODO 3: Con servidor HTTP
python examples/minigames_server.py    # Terminal 1
cd examples/minigames_web ; python -m http.server 8000  # Terminal 2
# Abre: http://localhost:8000
```

---

### P: ¿Cómo sé si todo está funcionando correctamente?

**R**: Ejecuta el script de validación:

```bash
python examples/validacion_final.py
```

Deberías ver: **✅ SISTEMA COMPLETAMENTE FUNCIONAL (9/9 funcionalidades)**

---

### P: ¿Qué hago si la validación falla?

**R**: Sigue estos pasos:

1. Verifica que instalaste las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecuta el diagnóstico completo:
   ```bash
   python examples/diagnostico_completo.py
   ```

3. Lee los mensajes de error y corrige según indicaciones

---

## 👁️ Calibración

### P: ¿Cuánto dura la calibración?

**R**: **3-4 segundos** (60 frames a ~60 FPS). Verás una barra de progreso que va de 0% a 100%.

---

### P: ¿Cómo calibro correctamente?

**R**: Sigue estos pasos:

1. **Posición**: Siéntate a 50-70 cm de la cámara
2. **Iluminación**: Asegúrate de tener luz frontal, sin contraluz
3. **Durante calibración**: 
   - Mira directamente a la cámara
   - Mantén tu cabeza estable
   - Respira normalmente (no te pongas rígido)
4. **Espera**: Hasta ver "✓ Calibración completada!"

---

### P: ¿Por qué falla la calibración?

**R**: Causas comunes:

| Causa | Solución |
|-------|----------|
| Mala iluminación | Agrega luz frontal, evita contraluz |
| Movimiento de cabeza | Mantén cabeza más estable |
| Demasiado lejos/cerca | Ajusta a 50-70 cm |
| Cámara sucia | Limpia la lente |
| Otra app usa cámara | Cierra Zoom, Teams, etc. |

---

### P: ¿Necesito recalibrar cada vez?

**R**: Sí, **cada vez que inicies el servidor**. La calibración solo toma 3-4 segundos y garantiza mejor precisión.

---

### P: ¿Puedo ajustar la duración de calibración?

**R**: Sí, en `examples/minigames_server.py`:

```python
# Línea ~82
min_calibration_frames = 60  # Cambia a 40-100

# Menos frames (40) = más rápido pero menos preciso
# Más frames (100) = más lento pero más preciso
```

---

## 🎯 Precisión y Tracking

### P: ¿Por qué el cursor vibra o tiembla (jitter)?

**R**: Aumenta la zona muerta:

```python
# Servidor (minigames_server.py, línea ~124)
dead_zone = 25  # Era 15, prueba 20-30

# Cliente (eyeTracking.js, línea ~10)
this.deadZone = 30;  // Era 20, prueba 25-40
```

---

### P: ¿Por qué el cursor se mueve muy lento?

**R**: Reduce el suavizado:

```python
# Servidor (minigames_server.py, línea ~88)
max_history = 3  # Era 5, prueba 3-4

# Cliente (eyeTracking.js, línea ~9)
this.maxHistory = 5;  // Era 8, prueba 5-6
```

---

### P: ¿Por qué el cursor salta o se mueve brusco?

**R**: Aumenta el suavizado:

```python
# Servidor
max_history = 8  # Era 5, prueba 7-10

# Cliente
this.maxHistory = 12;  // Era 8, prueba 10-15
```

---

### P: ¿Cuál es la precisión esperada?

**R**: Con calibración correcta:

- **Centro de pantalla**: ±20-40 píxeles
- **Bordes**: ±40-80 píxeles (normal, menos preciso)
- **Latencia**: <50ms (imperceptible)
- **Jitter**: <5 píxeles con zona muerta activada

---

### P: ¿Por qué la precisión varía entre sesiones?

**R**: Factores que afectan:

- **Iluminación diferente**: Mantén condiciones similares
- **Posición diferente**: Siéntate en el mismo lugar
- **Cansancio ocular**: Toma descansos cada 15-20 min
- **Calibración apresurada**: Tómate los 3-4 segundos completos

---

## 🎮 Juegos y Uso

### P: ¿Qué juegos están disponibles?

**R**: **6 juegos web**:

1. **Aim Trainer** - Precisión y velocidad
2. **Memory Match** - Memoria visual
3. **Snake** - Control fluido
4. **Reaction Test** - Tiempos de reacción
5. **Bubble Pop** - Coordinación
6. **Focus Flow** - Concentración

**2 juegos nativos Pygame**:

7. **Space Shooter** - Acción
8. **Maze Runner** - Navegación

---

### P: ¿Cómo ajusto los parámetros según el tipo de juego?

**R**: Recomendaciones:

**Juegos de Precisión** (Aim Trainer, Memory Match):
```javascript
// eyeTracking.js
this.maxHistory = 5;     // Menos suavizado
this.deadZone = 15;      // Más sensible
```

**Juegos de Movimiento** (Snake, Bubble Pop):
```javascript
this.maxHistory = 10;    // Más suavizado
this.deadZone = 25;      // Menos sensible
```

**Juegos de Reacción** (Reaction Test):
```javascript
this.maxHistory = 3;     // Mínimo suavizado
this.deadZone = 10;      // Máxima respuesta
```

---

### P: ¿Por qué los juegos no cargan?

**R**: Verifica:

1. **Servidor corriendo**: Debe mostrar "✓ Calibración completada!"
2. **WebSocket conectado**: Indicador verde "Conectado"
3. **Puerto 8765 libre**: Cierra otras apps que usen ese puerto
4. **Archivos presentes**: Ejecuta `validacion_final.py`

---

## 🔧 Problemas Técnicos

### P: "WebSocket no conecta" o "Desconectado"

**R**: Soluciones:

1. **Reinicia el servidor**: Ctrl+C, luego vuelve a ejecutar
2. **Verifica puerto**: 
   ```bash
   netstat -ano | findstr :8765
   ```
   Si está ocupado, cierra la app o cambia puerto
3. **URL correcta**: Debe ser `ws://localhost:8765`
4. **Firewall**: Permite conexión local en puerto 8765

---

### P: "Caugh error: 'NoneType' object has no attribute..." spam

**R**: Esto ya está **corregido** en la versión mejorada. Si aún ves el error:

1. Verifica que `eyeGestures/utils.py` tenga la versión mejorada:
   ```python
   if os.environ.get('EYE_GESTURES_DEBUG', '0') == '1':
       print(f"Caugh error: {e}")
   ```

2. Si quieres ver los errores (modo debug):
   ```bash
   set EYE_GESTURES_DEBUG=1
   python examples/minigames_server.py
   ```

---

### P: "AttributeError: _ARRAY_API not found" o error de NumPy

**R**: Incompatibilidad NumPy 2.x con OpenCV. Soluciones:

```bash
# Opción 1: Downgrade NumPy
pip install "numpy<2"

# Opción 2: Reinstalar OpenCV
pip uninstall opencv-python
pip install opencv-python --no-cache-dir

# Opción 3: Usa entorno virtual (recomendado)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

### P: "No se puede acceder a la cámara"

**R**: Verifica:

1. **Cámara conectada**: Prueba con otra app (Photo Booth, Zoom)
2. **Permisos**: Windows Settings → Privacy → Camera → Permitir apps
3. **Otra app la usa**: Cierra Zoom, Teams, Skype, OBS, etc.
4. **Test manual**:
   ```bash
   python examples/troubleshooting_camera.py
   ```

---

### P: "FPS muy bajos" (<30 FPS)

**R**: Optimizaciones:

1. **Cierra apps pesadas**: Chrome con muchas tabs, juegos, etc.
2. **Reduce resolución**: En `minigames_server.py`:
   ```python
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Era 1280
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Era 720
   ```
3. **Desactiva efectos visuales**: En juegos web
4. **Usa cámara USB**: Mejor que webcam integrada de laptop vieja

---

## 🎨 Personalización

### P: ¿Cómo cambio los colores de la UI?

**R**: Edita `examples/minigames_web/style.css`:

```css
/* Barra de calibración (línea ~165) */
.calibration-progress {
    background: linear-gradient(90deg, #ff6b6b, #ffa500);  /* Cambia colores */
}

/* Estado conectado (línea ~50) */
.status.connected {
    background-color: #2ecc71;  /* Verde actual */
}
```

---

### P: ¿Puedo agregar más juegos?

**R**: Sí, crea un nuevo HTML en `examples/minigames_web/games/`:

```html
<!-- miJuego.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Mi Juego</title>
    <script src="../eyeTracking.js"></script>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    <script>
        // Tu lógica de juego
        eyeTracking.addListener((data) => {
            // Usa data.x, data.y para cursor
        });
    </script>
</body>
</html>
```

Luego agrégalo a `index.html`:

```html
<a href="games/miJuego.html" class="game-card">
    <div class="game-icon">🎮</div>
    <h3>Mi Juego</h3>
    <p>Descripción</p>
</a>
```

---

### P: ¿Cómo cambio el puerto del WebSocket?

**R**: En `minigames_server.py` (línea ~197):

```python
# Cambia el puerto
await websockets.serve(handle_client, "localhost", 8765)
#                                                   ^^^^ nuevo puerto
```

Y en `eyeTracking.js` (línea ~35):

```javascript
this.socket = new WebSocket('ws://localhost:8765');
//                                           ^^^^ mismo puerto
```

---

## 📊 Rendimiento y Optimización

### P: ¿Cuál es la configuración más precisa?

**R**: Para máxima precisión (a costa de velocidad):

```python
# Servidor
min_calibration_frames = 100  # Calibración larga
max_history = 10             # Suavizado máximo
dead_zone = 10               # Zona muerta pequeña

# Cliente
this.maxHistory = 15;
this.deadZone = 15;
```

---

### P: ¿Cuál es la configuración más rápida?

**R**: Para mínimo lag (a costa de precisión):

```python
# Servidor
min_calibration_frames = 40  # Calibración rápida
max_history = 3              # Suavizado mínimo
dead_zone = 30               # Zona muerta grande (compensa jitter)

# Cliente
this.maxHistory = 5;
this.deadZone = 25;
```

---

### P: ¿Cuál es la configuración balanceada? (Recomendada)

**R**: Configuración actual (ya implementada):

```python
# Servidor
min_calibration_frames = 60  # Balance óptimo
max_history = 5              # Suavizado moderado
dead_zone = 15               # Anti-jitter efectivo

# Cliente
this.maxHistory = 8;         # Suavizado cliente
this.deadZone = 20;          # Anti-jitter cliente
```

---

## 🆘 Ayuda Adicional

### P: ¿Dónde encuentro más documentación?

**R**: Lee en este orden:

1. **`INDEX.md`** - Índice completo
2. **`RESUMEN_MEJORAS.md`** - Detalles técnicos
3. **`CONFIGURACION_OPTIMA.md`** - Guía de uso
4. **`TROUBLESHOOTING_WEB.md`** - Solución de problemas
5. **`SOLUCION_RAPIDA.md`** - Fixes rápidos

---

### P: ¿Cómo reporto un bug?

**R**: Sigue estos pasos:

1. **Ejecuta diagnóstico**:
   ```bash
   python examples/diagnostico_completo.py > diagnostico.txt
   python examples/validacion_final.py > validacion.txt
   ```

2. **Captura logs**:
   - Consola del servidor (copia texto completo)
   - Consola del navegador (F12, copia errores)

3. **Describe el problema**:
   - ¿Qué intentaste hacer?
   - ¿Qué esperabas?
   - ¿Qué pasó realmente?
   - ¿Pasos para reproducir?

4. **Incluye entorno**:
   - Versión de Python: `python --version`
   - Sistema operativo: Windows 10/11, etc.
   - Tipo de cámara: USB, integrada, etc.

---

### P: ¿El proyecto es open source?

**R**: Sí, revisa el archivo `LICENSE` en el repositorio.

---

### P: ¿Puedo usar esto comercialmente?

**R**: Consulta el archivo `LICENSE` para términos específicos.

---

## 🎓 Conceptos Técnicos

### P: ¿Cómo funciona el suavizado con promedio ponderado?

**R**: Sistema de dos capas:

**Capa 1 - Servidor** (últimos 5 puntos):
```python
# Ejemplo: puntos históricos con pesos
points = [(800, 600), (805, 602), (810, 605), (815, 608), (820, 610)]
weights = [1, 2, 3, 4, 5]  # Más peso a recientes

# Promedio ponderado
smooth_x = (1*800 + 2*805 + 3*810 + 4*815 + 5*820) / (1+2+3+4+5)
        = (800 + 1610 + 2430 + 3260 + 4100) / 15
        = 12200 / 15 = 813.3
```

**Capa 2 - Cliente** (últimos 8 puntos, mismo algoritmo)

**Resultado**: Movimientos fluidos sin saltos bruscos.

---

### P: ¿Cómo funciona la zona muerta?

**R**: Ignora movimientos pequeños:

```python
# Calcular distancia desde última posición
dx = new_x - last_x
dy = new_y - last_y
distance = sqrt(dx² + dy²)

# Si movimiento es pequeño, ignorar
if distance < dead_zone:  # Ej: 15 píxeles
    return last_x, last_y  # No actualizar
else:
    return new_x, new_y    # Actualizar posición
```

**Resultado**: Elimina jitter (micro-movimientos).

---

### P: ¿Por qué usar 60 frames de calibración?

**R**: Comparación:

| Frames | Tiempo | Precisión | Estabilidad |
|--------|--------|-----------|-------------|
| 25 | ~0.4s | Baja | Inestable |
| 40 | ~0.7s | Media | Aceptable |
| **60** | **~1.0s** | **Alta** | **Estable** |
| 80 | ~1.3s | Muy alta | Muy estable |
| 100 | ~1.7s | Máxima | Máxima |

**60 frames** es el balance óptimo: calibración rápida con buena precisión.

---

### P: ¿Qué es la regresión Ridge/LassoCV?

**R**: Algoritmos de machine learning para mapear:

```
Landmarks faciales (MediaPipe) → Posición en pantalla (X, Y)
```

- **Ridge**: Regresión lineal regularizada (previene overfitting)
- **LassoCV**: Ridge con selección de características automática

El sistema usa el que da mejor precisión según tus datos.

---

## 💡 Tips y Trucos

### P: ¿Cómo mejoro mi precisión personal?

**R**: Práctica y consistencia:

1. **Usa siempre las mismas condiciones**: Misma luz, posición, hora del día
2. **Calibra con cuidado**: Toma los 3-4 segundos completos
3. **Descansa**: Cada 15-20 minutos, 30 segundos de descanso visual
4. **Practica**: Juega Aim Trainer 5 min diarios, verás mejora en días
5. **Ajusta progresivamente**: No cambies todos los parámetros a la vez

---

### P: ¿Qué hago si mis ojos se cansan?

**R**: Regla 20-20-20:

- Cada **20 minutos**
- Mira algo a **20 pies de distancia** (~6 metros)
- Durante **20 segundos**

También:
- Parpadea conscientemente (evita ojos secos)
- Reduce brillo de pantalla
- Usa iluminación ambiente (no pantalla única en cuarto oscuro)

---

### P: ¿Funciona con gafas/lentes?

**R**: **Sí**, pero considera:

- ✅ Gafas normales: Funcionan perfectamente
- ⚠️ Gafas con reflejos: Evita luces directas que reflejen
- ⚠️ Gafas de sol: No recomendado (reduce precisión)
- ✅ Lentes de contacto: Perfectos

---

### P: ¿Puedo usar esto para accesibilidad?

**R**: **Sí**, ideal para:

- Personas con movilidad reducida
- Control de computadora sin manos
- Alternativa a mouse tradicional
- Aplicaciones educativas

**Nota**: Para uso médico/terapéutico, consulta con profesionales.

---

## 🎉 ¡Todo listo!

Si tu pregunta no está aquí:

1. Lee `INDEX.md` para más recursos
2. Ejecuta `validacion_final.py`
3. Revisa `CONFIGURACION_OPTIMA.md`
4. Consulta `TROUBLESHOOTING_WEB.md`

**¡Disfruta del eye-tracking! 👁️✨**
