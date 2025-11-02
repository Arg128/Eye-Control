# 🎮 EyeGestures Minigames

Una colección de minijuegos interactivos controlados completamente con la mirada, construidos sobre [EyeGesturesLite](https://github.com/NativeSensors/EyeGesturesLite).

## ✨ Características

### 🎯 Control por Mirada
Todos los juegos se controlan **100% con tu mirada** usando la cámara web. No necesitas mouse, teclado ni ningún hardware especial.

### 📊 Sistema de Tracking de Atención
- **Tiempo en página**: Rastrea cuánto tiempo has estado en la aplicación
- **Detección de atención**: Detecta cuando estás mirando la pantalla vs. cuando miras hacia otro lado
- **Estadísticas en tiempo real**: Panel visible con métricas de atención
- **Porcentaje de atención**: Calcula tu nivel de concentración

### 🎮 4 Minijuegos Incluidos

#### 🏓 Eye Pong
Juego clásico de Pong donde controlas la paleta moviendo tu mirada arriba y abajo. Compite contra la IA y trata de mantener la pelota en juego.

#### 🎯 Eye Target
Dispara a los objetivos mirándolos durante 1 segundo. Cada objetivo tiene un valor de puntos diferente. ¡Mientras más rápido, más puntos!

#### 🐍 Eye Snake
El clásico juego de la serpiente, pero controlado con tu mirada. Mira en la dirección que quieres que vaya la serpiente y recoge comida para crecer.

#### ⭐ Eye Collect
Recoge estrellas doradas mientras evitas obstáculos rojos. Tienes 60 segundos para conseguir la mayor puntuación posible.

## 🚀 Cómo Usar

### Opción 1: Abrir Directamente
1. Abre el archivo `minigames/index.html` en tu navegador
2. Permite el acceso a la cámara cuando se solicite
3. Selecciona un juego
4. Completa la calibración (mira los 25 círculos rojos)
5. ¡Juega!

### Opción 2: Servidor Local
```bash
# Usando Python
python -m http.server 8000

# O usando Node.js
npx http-server

# Luego abre en tu navegador
# http://localhost:8000/minigames/
```

## 📋 Requisitos

- Navegador moderno (Chrome, Edge, Firefox)
- Cámara web funcional
- Conexión HTTPS o localhost (requerido para acceso a cámara)
- Buena iluminación en tu rostro
- Permiso de cámara otorgado

## 🎯 Sistema de Calibración

Antes de jugar por primera vez, necesitas calibrar tu mirada:

1. Aparecerán **25 círculos rojos** uno a la vez
2. **Mira fijamente** cada círculo hasta que desaparezca
3. Mantén tu cabeza relativamente quieta
4. El cursor azul comenzará a seguir tu mirada
5. Después de los 25 puntos, ¡estarás listo para jugar!

**Consejos para mejor calibración:**
- Siéntate a una distancia cómoda de la pantalla
- Asegúrate de tener buena iluminación en tu cara
- Evita usar lentes de sol o sombreros
- Mantén tu cabeza estable

## 📊 Panel de Estadísticas

En la esquina superior derecha verás:

- **⏱️ Tiempo en página**: Cuánto tiempo has estado usando la app
- **👁️ Estado**: Si estás mirando la pantalla o no
- **📊 Tiempo mirando**: Tiempo total que has estado mirando
- **😔 Tiempo fuera**: Tiempo que no has estado mirando
- **📈 % Atención**: Porcentaje de atención calculado

### ¿Cómo funciona la detección?

El sistema detecta que **NO estás mirando** cuando:
- No hay movimiento de ojos detectado por más de 2 segundos
- La pestaña está oculta o minimizada
- No hay actividad de la cámara

## 🛠️ Tecnologías

- **EyeGesturesLite**: Librería de seguimiento ocular
- **MediaPipe**: Detección facial y ocular
- **Canvas API**: Renderizado de juegos
- **JavaScript ES6**: Lógica de juegos
- **CSS3**: Animaciones y estilos modernos

## 📁 Estructura del Proyecto

```
minigames/
├── index.html          # Página principal
├── main.js            # Controlador principal
├── timeTracker.js     # Sistema de tracking de tiempo
├── styles.css         # Estilos principales
└── games/
    ├── pong.js        # Juego de Pong
    ├── target.js      # Juego de disparos
    ├── snake.js       # Juego de serpiente
    └── collect.js     # Juego de recolección
```

## 🎨 Personalización

Puedes modificar fácilmente:

### Dificultad de Juegos
En cada archivo de juego (`games/*.js`):
- Velocidad de movimiento
- Tamaño de objetivos
- Tiempo límite
- Puntuaciones

### Colores y Estilos
En `styles.css`:
- Colores del tema
- Animaciones
- Diseño de tarjetas

### Detección de Atención
En `timeTracker.js`:
- `gazeTimeout`: Tiempo sin mirada para considerar "fuera"
- Frecuencia de actualización
- Cálculos de porcentaje

## 🐛 Solución de Problemas

### La cámara no funciona
- Verifica que otorgaste permisos de cámara
- Usa HTTPS o localhost
- Prueba otro navegador
- Verifica que ninguna otra app esté usando la cámara

### La calibración no funciona bien
- Mejora la iluminación
- Mira directamente cada círculo rojo
- Mantén tu cabeza quieta
- Siéntate más cerca/lejos de la pantalla

### El cursor no sigue bien mi mirada
- Recalibra (vuelve al menú y entra de nuevo)
- Ajusta tu posición
- Verifica la iluminación
- Limpia tu webcam

### Juegos muy lentos
- Cierra otras pestañas
- Actualiza tu navegador
- Verifica el rendimiento de tu computadora

## 📝 Notas

- La primera calibración puede tomar un minuto, ¡sé paciente!
- Entre más uses el sistema, mejor entenderá tu mirada
- Funciona mejor con buena iluminación
- Diseñado para ser accesible y divertido

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Puedes:
- Añadir nuevos juegos
- Mejorar la detección de atención
- Optimizar el rendimiento
- Mejorar la UI/UX
- Reportar bugs

## 📄 Licencia

Este proyecto utiliza EyeGesturesLite. Consulta la licencia del proyecto principal.

## 🙏 Créditos

- Basado en [EyeGesturesLite](https://github.com/NativeSensors/EyeGestures)
- Detección facial por MediaPipe
- Desarrollado con ❤️ para accesibilidad

---

**¡Diviértete jugando con tu mirada! 👀🎮**
