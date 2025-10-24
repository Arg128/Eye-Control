# 🎯 Guía de Configuración Óptima - EyeGestures

## ✨ Mejoras Implementadas

### 1. **Calibración Extendida y de Alta Calidad**
- ✅ Aumentada de 25 a 60 frames para mejor precisión
- ✅ Progreso visual en tiempo real
- ✅ Validación de calidad de datos
- ✅ Mensajes informativos durante calibración

### 2. **Suavizado Avanzado de Datos**
- ✅ Buffer de historial (8 puntos)
- ✅ Promedio ponderado (más peso a datos recientes)
- ✅ Zona muerta de 15-20 píxeles para reducir jitter
- ✅ Filtrado temporal para movimientos suaves

### 3. **Interfaz Mejorada**
- ✅ Indicador visual de calibración con barra de progreso
- ✅ Estado de conexión claro
- ✅ Feedback inmediato en la web

### 4. **Optimización de Comunicación**
- ✅ WebSocket con reconexión automática
- ✅ Keepalive para mantener conexión estable
- ✅ Manejo robusto de errores sin spam en consola

---

## 🎮 Configuración Óptima para Juegos

### Posición y Entorno

1. **Distancia de la cámara**: 50-70 cm
2. **Ángulo**: Cámara a la altura de tus ojos o ligeramente superior
3. **Iluminación**: 
   - ✅ Luz frontal o lateral suave
   - ❌ Evita contraluz (luz detrás de ti)
   - ✅ Iluminación uniforme en tu rostro

4. **Posición de cabeza**:
   - ✅ Mantén la cabeza relativamente estable
   - ✅ Movimientos naturales están bien
   - ❌ Evita movimientos bruscos durante calibración

### Calibración (Primera Vez)

1. **Inicia el servidor**:
   ```bash
   python examples/minigames_server.py
   ```

2. **Espera el mensaje de calibración**:
   ```
   → Iniciando calibración extendida (60 frames)...
     Mantén tu cabeza estable y mira directamente a la cámara
   ```

3. **Durante los primeros 3-4 segundos**:
   - Mira directamente a la cámara
   - Mantén tu cabeza lo más estable posible
   - Respira normalmente (no te pongas rígido)

4. **Verás el progreso**:
   ```
   Calibrando: 10/60 (17%)
   Calibrando: 20/60 (33%)
   ...
   Calibrando: 60/60 (100%)
   ✓ Calibración completada!
   → Modo tracking activado
   ```

5. **Abre la página web**: El indicador mostrará "Conectado" en verde

---

## 🎯 Ajustes de Sensibilidad

### En el Servidor (`minigames_server.py`)

```python
# Suavizado de datos (línea ~88)
max_history = 5  # Aumenta para más suavizado (3-10)
                 # Valor actual: 5 (balance óptimo)

# Zona muerta (línea ~124)
dead_zone = 15   # Aumenta para menos jitter (10-30)
                 # Valor actual: 15 (recomendado)

# Calibración (línea ~82)
min_calibration_frames = 60  # Más frames = mejor calibración
                             # Rango: 40-100
```

### En el Cliente Web (`eyeTracking.js`)

```javascript
// Suavizado (línea ~9)
this.maxHistory = 8;    // Aumenta para más suavizado (5-15)
                        // Valor actual: 8 (óptimo)

// Zona muerta (línea ~10)
this.deadZone = 20;     // Aumenta para menos jitter (15-40)
                        // Valor actual: 20 (recomendado)
```

---

## 🔧 Parámetros por Tipo de Juego

### Juegos de Precisión (Aim Trainer, Memory Match)
```javascript
// En eyeTracking.js
this.maxHistory = 5;    // Menos suavizado, más responsive
this.deadZone = 15;     // Menor zona muerta
```

### Juegos de Movimiento (Snake, Bubble Pop)
```javascript
// En eyeTracking.js
this.maxHistory = 10;   // Más suavizado, movimientos fluidos
this.deadZone = 25;     // Mayor zona muerta
```

### Juegos de Reacción (Reaction Test)
```javascript
// En eyeTracking.js
this.maxHistory = 3;    // Mínimo suavizado
this.deadZone = 10;     // Zona muerta pequeña
```

---

## 🚀 Inicio Rápido Optimizado

### Método 1: Script Automático
```bash
cd examples
start_web_minigames_v2.bat
```
Todo se configura automáticamente.

### Método 2: Manual Optimizado
```bash
# Terminal 1 - Servidor con calibración extendida
python examples/minigames_server.py

# Espera a ver "✓ Calibración completada!"
# Luego abre en navegador:
examples/minigames_web/index.html
```

---

## 📊 Verificación de Calidad

### Señales de Buena Calibración:
- ✅ Cursor se mueve suavemente sin saltos
- ✅ Sigue tu mirada con precisión ±30 píxeles
- ✅ Zona central más precisa que bordes (normal)
- ✅ Sin jitter (vibración) excesivo
- ✅ Respuesta rápida (<100ms lag perceptible)

### Señales de Mala Calibración:
- ❌ Cursor salta erráticamente
- ❌ Gran desfase (>100 píxeles)
- ❌ Jitter extremo
- ❌ Lag notable (>300ms)
- ❌ Cursor se va a las esquinas

### Si la calibración es mala:
1. **Reinicia el servidor** (Ctrl+C, luego vuelve a iniciar)
2. **Mejora la iluminación**
3. **Ajusta tu posición** (más cerca/lejos)
4. **Limpia la lente de tu cámara**
5. **Cierra otras apps** que usen la cámara

---

## 🎨 Personalización Avanzada

### Cambiar Parámetros de Detección

En `eyeGestures/face.py` (línea 13):
```python
self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
    refine_landmarks=True,
    static_image_mode=False,
    min_detection_confidence=0.5,  # Aumenta para ser más estricto (0.3-0.9)
    min_tracking_confidence=0.5    # Aumenta para tracking más estable (0.3-0.9)
)
```

### Ajustar Algoritmo de Regresión

En `eyeGestures/calibration_v2.py`:
```python
# El sistema usa Ridge o LassoCV automáticamente
# Para forzar uno específico, modifica el código de auto-selección
```

---

## 📈 Métricas de Rendimiento

### Valores Óptimos:
- **FPS**: 50-60 (servidor y cliente)
- **Latencia**: <50ms (red local)
- **Precisión**: ±20-40 píxeles en centro
- **Estabilidad**: <5 píxeles de jitter
- **Tasa de detección**: >95% de frames

### Monitoreo:
```bash
# En consola del servidor verás:
[TRACKING] Gaze: (856, 432) | Fixation: 0.67 | Clients: 1

# En consola del navegador (F12):
# Posición X/Y se actualiza en tiempo real
```

---

## 🆘 Troubleshooting Específico

### "El cursor no sigue bien mi mirada"
1. **Recalibra**: Reinicia el servidor
2. **Verifica posición**: 50-70cm, centrado
3. **Iluminación**: Luz frontal suave
4. **Aumenta calibración**: Cambia a 80-100 frames

### "Mucho jitter (vibración)"
1. **Aumenta suavizado**: `maxHistory = 10`
2. **Aumenta zona muerta**: `deadZone = 30`
3. **Mejora iluminación**: Reduce sombras

### "Lag notable"
1. **Reduce historial**: `maxHistory = 3`
2. **Verifica CPU**: Cierra apps pesadas
3. **Simplifica juego**: Menos elementos en pantalla

### "Cursor va a las esquinas"
1. **Recalibra completamente**
2. **Verifica que el rostro esté completo en cámara**
3. **Aumenta confianza de detección**: 0.5 → 0.7

---

## 🎯 Recomendaciones Finales

### Para Mejor Experiencia:

1. **Calibra cada sesión**: 3-4 segundos bien invertidos
2. **Mantén condiciones constantes**: Misma luz, posición
3. **Tómate descansos**: Cada 15-20 minutos
4. **Experimenta con parámetros**: Encuentra tu configuración ideal
5. **Feedback**: Reporta problemas para mejorar el sistema

### Configuración Recomendada (Punto de Partida):
```python
# Servidor
max_history = 5
dead_zone = 15
min_calibration_frames = 60

# Cliente
maxHistory = 8
deadZone = 20
```

---

## 📞 Soporte

Si después de seguir esta guía sigues teniendo problemas:

1. Ejecuta diagnóstico:
   ```bash
   python examples/diagnostico_completo.py
   ```

2. Lee guías:
   - `TROUBLESHOOTING_WEB.md`
   - `SOLUCION_RAPIDA.md`

3. Verifica logs del servidor y navegador (F12)

---

**¡Disfruta de la experiencia mejorada de eye-tracking! 🎮👁️✨**
