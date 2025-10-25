# 🚀 Inicio Rápido - Funciones Avanzadas

## ⚡ Empezar en 3 Pasos

### 1️⃣ Inicia el Servidor
```bash
npm start
```
O haz doble clic en `START_MINIGAMES.bat`

### 2️⃣ Prueba la Cámara
- Haz clic en **"🔍 Probar Cámara"**
- Autoriza el acceso a la cámara
- Verifica que tu rostro sea detectado

### 3️⃣ Activa las Funciones
Usa el panel **⚙️ Controles Avanzados** (esquina superior izquierda):

```
┌─────────────────────────────┐
│ ⚙️ Controles Avanzados      │
├─────────────────────────────┤
│ [👁️ Rastro de Mirada: OFF] │ ← Activa el rastro visual
│ [🔥 Heatmap: OFF]           │ ← Activa el mapa de calor
│ [📖 Modo Lectura: OFF]      │ ← Detecta cuando lees
│ [🗑️ Limpiar Rastro]         │ ← Borra el historial
│ 📊 Precisión: [====|----]   │ ← Ajusta el filtro
└─────────────────────────────┘
```

---

## 🎯 Probar Cada Función

### ✅ Rastro de Mirada

1. Activa **"👁️ Rastro de Mirada"**
2. Mueve tus ojos por la pantalla
3. Verás puntos luminosos siguiendo tu mirada
4. Los puntos desaparecen después de 3 segundos

**Prueba esto:**
- Dibuja círculos con la mirada
- Escribe letras mirando
- Observa cómo el rastro sigue tu movimiento

### ✅ Heatmap

1. Activa primero el **Rastro de Mirada**
2. Luego activa **"🔥 Heatmap"**
3. Mira diferentes zonas de la pantalla
4. Verás colores indicando zonas más miradas:
   - 🔵 **Azul** = Poco mirado
   - 🟢 **Verde** = Mirado moderadamente
   - 🟡 **Amarillo** = Mirado frecuentemente
   - 🔴 **Rojo** = Muy mirado

**Prueba esto:**
- Mira un área específica repetidamente
- Observa cómo se calienta el color
- Útil para analizar patrones de atención

### ✅ Modo Lectura

1. Activa **"📖 Modo Lectura"**
2. Abre un documento o página con texto
3. Lee normalmente de izquierda a derecha
4. El sistema detectará automáticamente:
   - ✅ Cuando empiezas a leer
   - 📊 Cuántas líneas lees
   - ⏱️ Tu velocidad de lectura
   - 📈 Tu patrón de movimiento ocular

**Panel de estadísticas (esquina superior derecha):**
```
📖 Modo Lectura
├─ Estado: ✅ Leyendo
├─ Tiempo leyendo: 1m 23s
├─ Líneas leídas: 28
├─ Palabras/min: 245
└─ Patrón: 78% →
```

**Prueba esto:**
- Lee este documento
- Observa cómo detecta cambios de línea
- Compara tu WPM con el promedio (200-250)

### ✅ Filtro de Precisión

El slider **"📊 Precisión del Filtro"** controla el suavizado:

| Valor | Efecto | Uso Recomendado |
|-------|--------|-----------------|
| 1-3 | Muy suave | Fotos/imágenes estáticas |
| 4-7 | **Óptimo** | **Uso general y juegos** |
| 8-12 | Reactivo | Movimientos rápidos |
| 13-20 | Crudo | Debugging/desarrollo |

**Prueba esto:**
1. Pon el slider en 20 (máximo)
2. Observa el temblor en el rastro
3. Bájalo a 5
4. Nota cómo se suaviza el movimiento

---

## 🎮 Probar con Juegos

### Eye Pong
1. Selecciona **Eye Pong**
2. Activa el **Rastro de Mirada**
3. Observa cómo tu mirada controla la paleta
4. El filtro suaviza los movimientos bruscos

### Eye Target
1. Selecciona **Eye Target**
2. Activa el **Heatmap**
3. Dispara mirando los objetivos
4. El heatmap muestra dónde has mirado más

### Eye Snake
1. Selecciona **Eye Snake**
2. Usa un filtro medio (5-7)
3. Controla la serpiente con la mirada
4. El filtro previene movimientos accidentales

### Eye Collect
1. Selecciona **Eye Collect**
2. Activa el **Rastro**
3. Recoge estrellas con tu mirada
4. Evita obstáculos

---

## 🧪 Experimentos Sugeridos

### Experimento 1: Medir tu Velocidad de Lectura
```
1. Activa Modo Lectura
2. Abre FUNCIONES_AVANZADAS.md
3. Lee durante 2 minutos
4. Anota tu WPM
5. Compara con:
   - Lento: < 200 WPM
   - Promedio: 200-300 WPM
   - Rápido: 300-500 WPM
   - Muy rápido: > 500 WPM
```

### Experimento 2: Crear Arte con la Mirada
```
1. Activa Rastro + Heatmap
2. "Dibuja" con tu mirada:
   - Tu nombre
   - Una casa
   - Un rostro
   - Figuras geométricas
3. Captura pantalla del resultado
4. Limpia y repite
```

### Experimento 3: Analizar Precisión
```
1. Pon filtro en 20 (sin filtrado)
2. Intenta mirar un punto fijo 10 segundos
3. Observa el temblor natural del ojo
4. Baja filtro a 5
5. Repite - nota la diferencia
```

### Experimento 4: Medir Atención
```
1. Abre una página web
2. Activa Heatmap
3. Navega normalmente 2 minutos
4. Observa el mapa de calor:
   - ¿Dónde miraste más?
   - ¿Qué ignoraste?
   - ¿Patrón F (típico de lectura web)?
```

---

## 🎯 Calibración para Máxima Precisión

### Preparación
- 💡 Iluminación: Luz frontal, evita ventanas detrás
- 📏 Distancia: 50-70cm de la pantalla
- 🪑 Postura: Siéntate derecho, cabeza estable
- 👓 Gafas: Pueden afectar precisión, prueba con/sin

### Proceso
1. Haz clic en un juego
2. Aparecerá **"Calibración Mejorada"**
3. Selecciona modo:
   - **Estándar (25 puntos)**: Rápido, preciso
   - **Extendido (49 puntos)**: Lento, muy preciso
4. Haz clic **"▶️ Comenzar Calibración"**
5. Mira cada círculo rojo fijamente
6. No muevas los ojos hasta que cambie
7. ¡Listo! 🎉

### Problemas Comunes

| Problema | Solución |
|----------|----------|
| 😵 Mirada desviada | Recalibra |
| 🤪 Saltos aleatorios | Aumenta valor filtro |
| 🐌 Respuesta lenta | Disminuye valor filtro |
| 😣 No detecta rostro | Mejora iluminación |
| 🤷 Calibración falla | Mantén cabeza quieta |

---

## 📊 Interpretar Estadísticas

### Panel de Atención
```
⏱️ Tiempo en página: 5m 32s     ← Tiempo total
👁️ Estado: Mirando               ← Estado actual
📊 Tiempo mirando: 5m 10s        ← Tiempo activo
😔 Tiempo fuera: 22s              ← Tiempo inactivo
📈 % Atención: 94%                ← Porcentaje activo
```

**Interpretación:**
- **> 90%**: Muy atento
- **70-90%**: Atento normal
- **50-70%**: Distraído
- **< 50%**: Muy distraído

### Panel de Lectura
```
📖 Modo Lectura
├─ Estado: ✅ Leyendo             ← Detectando lectura ahora
├─ Tiempo leyendo: 2m 15s        ← Tiempo acumulado
├─ Líneas leídas: 45              ← Saltos de línea detectados
├─ Palabras/min: 280              ← Velocidad estimada
└─ Patrón: 82% →                  ← % movimientos izq→der
```

**Patrón de movimiento:**
- **> 60%**: Claramente leyendo
- **40-60%**: Lectura irregular (escaneo)
- **< 40%**: No leyendo (navegando)

---

## 💡 Tips Profesionales

### Para Desarrolladores
```javascript
// Acceder a sistemas en consola
gazeFilter.getStats()        // Stats del filtro
gazeTrail.points             // Array de puntos
readingDetector.getStats()   // Stats de lectura
timeTracker.getStats()       // Stats de atención

// Cambiar colores del rastro
gazeTrail.setColor('rgba(255, 0, 0, 0.6)')  // Rojo

// Ajustar filtro programáticamente
gazeFilter.measurementNoise = 3  // Más suave
gazeFilter.reset()                // Reiniciar
```

### Para Usuarios
- 🎨 Usa colores contrastantes para mejor visibilidad
- 📱 Funciona mejor en pantallas grandes
- ⚡ Cierra otras apps que usen cámara
- 🔄 Recalibra cada 15-20 minutos
- 💾 Las calibraciones no se guardan (por ahora)

### Para Investigadores
- 📊 El heatmap usa grid de 40x40px
- 📈 Las estadísticas se actualizan cada frame
- 🧪 El filtro de Kalman usa modelo de velocidad constante
- 📝 La detección de lectura requiere mínimo 5 puntos
- ⏱️ El timestamp es en milisegundos (Date.now())

---

## 🆘 Solución de Problemas

### La cámara no se activa
1. ✅ Verifica permisos en navegador
2. ✅ Cierra Zoom/Teams/otras apps
3. ✅ Usa Chrome o Edge (recomendado)
4. ✅ Estás en localhost o HTTPS
5. ✅ Tu cámara funciona en otras apps

### El rastro no aparece
1. ✅ Haz clic en "Rastro de Mirada"
2. ✅ Completa la calibración primero
3. ✅ Mueve tus ojos por la pantalla
4. ✅ Verifica que el juego esté activo

### No detecta lectura
1. ✅ Activa "Modo Lectura"
2. ✅ Lee moviendo ojos izq→der
3. ✅ Haz saltos de línea visibles
4. ✅ Requiere al menos 2 segundos leyendo

### El movimiento es muy brusco
1. ✅ Baja el valor del filtro (1-5)
2. ✅ Mejora la iluminación
3. ✅ Recalibra el sistema
4. ✅ Mantén la cabeza más quieta

---

## 🎓 Siguiente Nivel

¿Quieres más? Lee la documentación completa:

- 📖 **FUNCIONES_AVANZADAS.md** - Guía técnica completa
- 📚 **README.md** - Información general del proyecto
- 🚀 **QUICKSTART.html** - Tutorial interactivo
- 💻 **Código fuente** - Explora los .js

---

## 🎉 ¡A Disfrutar!

Ya estás listo para aprovechar todas las funciones avanzadas:

✅ Rastro visual de tu mirada  
✅ Heatmap de zonas de atención  
✅ Detección automática de lectura  
✅ Filtrado inteligente para precisión  
✅ Calibración mejorada  
✅ Estadísticas en tiempo real  

**¡Diviértete explorando el poder del eye tracking! 👁️✨**

---

*Última actualización: Octubre 2025*
