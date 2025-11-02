# 🎯 EyeGestures Minigames - Funciones Avanzadas

## 📋 Índice
- [Nuevas Funciones](#nuevas-funciones)
- [Mejoras de Precisión](#mejoras-de-precisión)
- [Modo Lectura](#modo-lectura)
- [Rastro Visual](#rastro-visual)
- [Calibración Mejorada](#calibración-mejorada)
- [Controles](#controles)

---

## 🆕 Nuevas Funciones

### 1️⃣ **Rastro de Mirada (Gaze Trail)**
Visualiza en tiempo real dónde estás mirando con un rastro de puntos luminosos.

**Características:**
- 👁️ Rastro visual con fade automático
- 🔥 Modo Heatmap para ver zonas más miradas
- 🎨 Colores personalizables
- 📊 Hasta 50 puntos simultáneos
- ⚡ Rendimiento optimizado

**Cómo usar:**
1. Haz clic en el botón **"👁️ Rastro de Mirada"** en el panel de controles
2. Activa el **Heatmap** para ver un mapa de calor
3. Usa **"🗑️ Limpiar Rastro"** para borrar el historial

---

### 2️⃣ **Modo Lectura**
Detecta automáticamente cuando estás leyendo texto y proporciona estadísticas.

**Lo que detecta:**
- 📖 Inicio y fin de lectura
- 📝 Número de líneas leídas
- ⏱️ Tiempo total leyendo
- 📊 Palabras por minuto estimadas
- 🔄 Patrón de movimiento ocular

**Algoritmo de detección:**
- Analiza movimientos de izquierda a derecha
- Detecta saltos de línea (movimientos grandes hacia abajo-izquierda)
- Calcula ratio de movimientos típicos de lectura
- Activa cuando el ratio supera 40%

**Estadísticas mostradas:**
```
📖 Modo Lectura
├─ Estado: ✅ Leyendo / ⏸️ No leyendo
├─ Tiempo leyendo: 45s
├─ Líneas leídas: 12
├─ Palabras/min: 250
└─ Patrón: 75% →
```

---

### 3️⃣ **Filtro de Kalman Mejorado**
Sistema avanzado de filtrado para reducir ruido y mejorar precisión.

**Componentes:**
- **Filtro de Kalman**: Predice y suaviza movimientos
- **EMA (Exponential Moving Average)**: Suavizado adicional
- **Detección de Outliers**: Elimina saltos anormales
- **Buffer circular**: Mantiene estadísticas recientes

**Parámetros ajustables:**
- `processNoise`: Ruido del proceso (0.01 por defecto)
- `measurementNoise`: Ruido de medición (5 por defecto, ajustable con slider)
- `maxJumpDistance`: Distancia máxima permitida (300px)

**Mejoras de precisión:**
- ✅ Reduce jitter (temblor)
- ✅ Elimina saltos falsos
- ✅ Suaviza trayectorias
- ✅ Predice movimientos
- ✅ Mantiene latencia baja

**Control de precisión:**
Usa el slider **"📊 Precisión del Filtro"** (1-20):
- Valores bajos (1-5): Más suave, respuesta más lenta
- Valores medios (5-10): Balance óptimo
- Valores altos (10-20): Más reactivo, menos suavizado

---

### 4️⃣ **Calibración Mejorada**
Dos modos de calibración para diferentes necesidades.

#### Modo Estándar (25 puntos)
- ✅ Grid 5x5
- ⚡ Rápido (~40 segundos)
- 🎯 Precisión buena
- 👍 Recomendado para juegos

#### Modo Extendido (49 puntos)
- ✅ Grid 7x7
- ⏱️ Más lento (~75 segundos)
- 🎯 Precisión máxima
- 🔬 Recomendado para aplicaciones de precisión

**Características:**
- 📊 Barra de progreso en tiempo real
- ✅ Feedback visual por cada punto
- 🔄 Patrón zigzag optimizado (menos movimiento de ojos)
- 🎨 Interfaz mejorada con instrucciones claras

**Instrucciones de calibración:**
1. Mantén la cabeza quieta
2. Mira fijamente cada círculo rojo 🔴
3. El círculo azul 🔵 muestra tu mirada estimada
4. El sistema avanza automáticamente
5. No muevas los ojos hasta que cambie el punto

---

## 🎮 Controles Avanzados

### Panel de Controles
Ubicación: **Esquina superior izquierda**

```
⚙️ Controles Avanzados
├─ 👁️ Rastro de Mirada: ON/OFF
├─ 🔥 Heatmap: ON/OFF
├─ 📖 Modo Lectura: ON/OFF
├─ 🗑️ Limpiar Rastro
└─ 📊 Precisión del Filtro: [slider 1-20]
```

### Atajos y Consejos

**Para mejor precisión:**
1. Buena iluminación frontal
2. Evita luz de fondo (ventanas detrás)
3. Mantén distancia de 50-70cm de la pantalla
4. Ajusta el filtro según tu necesidad
5. Usa el modo de calibración extendido

**Problemas comunes:**
- **Saltos en la mirada**: Aumenta el valor del filtro
- **Respuesta lenta**: Disminuye el valor del filtro
- **Mirada desviada**: Recalibra el sistema
- **No detecta lectura**: Asegúrate de hacer movimientos de izquierda a derecha

---

## 📊 Estadísticas en Tiempo Real

### Panel de Atención (Derecha)
```
⏱️ Tiempo en página: 5m 32s
👁️ Estado: Mirando
📊 Tiempo mirando: 5m 10s
😔 Tiempo fuera: 22s
📈 % Atención: 94%
```

### Panel de Lectura (Derecha, cuando está activo)
```
📖 Modo Lectura
├─ Estado: ✅ Leyendo
├─ Tiempo leyendo: 2m 15s
├─ Líneas leídas: 45
├─ Palabras/min: 280
└─ Patrón: 82% →
```

---

## 🔧 Configuración Técnica

### Arquitectura del Sistema

```
┌─────────────────┐
│   EyeGestures   │ ← Sistema base de tracking
└────────┬────────┘
         │
    ┌────▼─────┐
    │   Filtro │ ← Filtro de Kalman + EMA
    │  Kalman  │
    └────┬─────┘
         │
    ┌────▼─────────────┬──────────────┬────────────┐
    │                  │              │            │
┌───▼────┐    ┌───────▼──────┐  ┌───▼────┐  ┌───▼────┐
│ Juegos │    │ Gaze Trail   │  │ Lect.  │  │  Time  │
│        │    │  + Heatmap   │  │ Detect │  │ Track  │
└────────┘    └──────────────┘  └────────┘  └────────┘
```

### Pipeline de Procesamiento

1. **Captura** (30 FPS)
   - MediaPipe FaceMesh detecta rostro
   - Extrae landmarks oculares

2. **Filtrado**
   - Filtro de Kalman predice posición
   - EMA suaviza resultado
   - Detecta y elimina outliers

3. **Distribución**
   - Envía a TimeTracker
   - Actualiza GazeTrail
   - Alimenta ReadingDetector
   - Pasa al juego actual

4. **Visualización**
   - Rastro en canvas overlay
   - Heatmap si está activado
   - Stats en paneles UI

---

## 🚀 Rendimiento

### Optimizaciones Implementadas

- ✅ **Canvas offscreen** para rastro
- ✅ **RequestAnimationFrame** para animaciones
- ✅ **Buffer circular** limitado (50 puntos max)
- ✅ **Fade automático** de puntos antiguos
- ✅ **Grid para heatmap** (reduce complejidad)
- ✅ **Throttling** de logs (cada 30 frames)

### Métricas Esperadas

| Métrica | Valor |
|---------|-------|
| FPS | 25-30 |
| Latencia | 30-50ms |
| CPU | 10-20% |
| RAM | 50-100MB |
| Precisión (calibrado) | ±20-40px |

---

## 🎯 Casos de Uso

### 1. Juegos
- Usa calibración estándar
- Activa rastro para debugging
- Filtro en valor medio (5-7)

### 2. Lectura de Documentos
- Activa modo lectura
- Usa heatmap para ver zonas más leídas
- Calibración extendida recomendada

### 3. Análisis de UX
- Activa heatmap
- Captura patrones de navegación
- Exporta estadísticas de lectura

### 4. Accesibilidad
- Calibración extendida
- Filtro alto para estabilidad
- Rastro visible como feedback

---

## 🐛 Debugging

### Console.log útiles

```javascript
// Ver stats del filtro (cada 30 frames)
📊 Filtro: {
  averageMovement: 15.2,
  maxMovement: 45.8,
  velocity: 234.5,
  stability: "Alta"
}

// Detección de lectura
📖 Lectura detectada
📕 Fin de lectura

// Outliers
Outlier detectado, usando predicción
```

### Verificar estado

```javascript
// En la consola del navegador:
gazeFilter.getStats()    // Estadísticas del filtro
gazeTrail.points.length  // Número de puntos en rastro
readingDetector.getStats()  // Estadísticas de lectura
```

---

## 📝 Notas Técnicas

### Filtro de Kalman

El filtro mantiene un vector de estado `[x, y, vx, vy]` donde:
- `x, y`: Posición actual
- `vx, vy`: Velocidad en cada eje

**Ecuaciones:**
- Predicción: `x' = x + vx*dt`
- Actualización: `x = x' + K*(medición - x')`
- Ganancia: `K = P / (P + R)` donde P=covarianza, R=ruido

### Detección de Lectura

**Criterios:**
- Ratio de movimientos izq→der > 40%
- Saltos de línea detectados (dx<-100, 20<dy<50)
- Movimientos horizontales dominantes
- Continuidad temporal

**Cálculo WPM:**
```
WPM = (líneas_leídas * 10) / (tiempo_minutos)
```
Asume ~10 palabras por línea promedio.

---

## 🤝 Contribuir

¿Tienes ideas para mejorar? Algunas sugerencias:

- 🎨 Más temas de color para rastro
- 📊 Exportar datos de heatmap
- 🎮 Más modos de calibración
- 📈 Gráficos de estadísticas
- 🔊 Feedback sonoro
- 💾 Guardar/cargar calibraciones

---

## 📄 Licencia

MIT License - Ver archivo LICENSE en la raíz del proyecto.

---

## 📞 Soporte

- 🐛 **Issues**: GitHub Issues
- 📧 **Email**: soporte@eyegestures.com
- 🌐 **Web**: https://eyegestures.com
- 💬 **Discord**: https://discord.gg/eyegestures

---

**¡Disfruta de la experiencia mejorada de Eye Tracking! 👁️✨**
