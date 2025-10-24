# 🎮 EyeGestures Launcher & Minigames

Sistema completo de lanzador profesional con minijuegos controlados por eye-tracking.

## 🚀 Características

### Launcher Profesional
- Interfaz gráfica moderna y elegante
- Acceso rápido a todos los componentes
- Animaciones suaves y efectos visuales
- Navegación intuitiva

### Minijuegos Web 🌐
Página web interactiva con 3 minijuegos completamente funcionales:

1. **🎯 Aim Trainer** - Entrena tu precisión apuntando a objetivos
2. **🧠 Memory Match** - Encuentra parejas de cartas con tu mirada
3. **💫 Bubble Pop** - Revienta burbujas mirándolas

### Minijuegos Nativos 🎮
Juegos nativos en pygame con eye-tracking:

1. **🚀 Space Shooter** - Dispara naves enemigas con tu mirada
2. **🌊 Maze Runner** - Navega por un laberinto de obstáculos

## 📦 Instalación

### Requisitos Adicionales
Además de los requisitos de EyeGestures, necesitas:

```bash
pip install websockets
```

## 🎯 Uso

### Opción 1: Usar el Launcher (Recomendado)

Ejecuta el launcher principal:

```bash
python examples/launcher.py
```

Desde el launcher puedes:
- ✅ Calibrar y probar el eye-tracking
- ✅ Jugar minijuegos web
- ✅ Jugar minijuegos nativos
- ✅ Ver demos básicos

### Opción 2: Ejecutar Componentes Individualmente

#### Calibración y Tracking
```bash
python examples/simple_example_v2.py
```

#### Minijuegos Web
1. Inicia el servidor de eye-tracking:
```bash
python examples/minigames_server.py
```

2. Abre en tu navegador:
```
examples/minigames_web/index.html
```

#### Minijuegos Pygame
```bash
python examples/minigames_pygame.py
```

## 🎮 Controles

### Eye-Tracking
- **Mirada**: Controla el cursor/posición
- **Fijación (1 segundo)**: Interactúa con objetos
- **ESC**: Volver al menú principal

### Modo Fallback (Ratón)
Si el eye-tracking no está conectado, el sistema automáticamente usa el ratón:
- **Movimiento**: Controla la posición
- **Click sostenido**: Simula fijación

## 🌐 Minijuegos Web - Detalles

### Aim Trainer
- Duración: 60 segundos
- Objetivo: Maximiza tu puntuación
- Control: Mira el objetivo por 0.5s para acertar

### Memory Match
- 16 cartas (8 parejas)
- Control: Mira una carta por 0.8s para voltearla
- Encuentra todas las parejas

### Bubble Pop
- Burbujas infinitas
- Control: Mira una burbuja por 1s para reventarla
- Las burbujas suben continuamente

## 🎮 Minijuegos Pygame - Detalles

### Space Shooter
- Control de nave: Mueve tu mirada horizontalmente
- Disparo: Mantén la mirada fija (fixation > 0.8)
- Objetivo: Destruye naves enemigas

### Maze Runner
- Control: Mueve la bola verticalmente con tu mirada
- Objetivo: Evita los obstáculos
- La velocidad aumenta progresivamente

## 🔧 Configuración

### Ajustar Resolución
Edita en `minigames_server.py`:
```python
screen_width = 1920  # Tu ancho de pantalla
screen_height = 1080  # Tu alto de pantalla
```

### Puerto WebSocket
Por defecto usa `ws://localhost:8765`. Para cambiar:
- Server: `minigames_server.py` línea `websockets.serve(register, "localhost", 8765)`
- Cliente: `eyeTracking.js` línea `this.ws = new WebSocket('ws://localhost:8765')`

## 🐛 Solución de Problemas

### El eye-tracking no conecta
1. Verifica que la cámara esté disponible
2. Ejecuta `python examples/troubleshooting_camera.py`
3. Asegúrate de que solo una aplicación use la cámara

### Los minijuegos web no funcionan
1. Verifica que el servidor esté corriendo
2. Abre la consola del navegador (F12) para ver errores
3. El modo mouse funciona como fallback automático

### Performance lento
1. Cierra otras aplicaciones
2. Reduce la resolución de la cámara
3. Ajusta el FPS en el código

## 📝 Estructura de Archivos

```
examples/
├── launcher.py                    # Launcher principal
├── simple_example_v2.py          # Demo con interfaz mejorada
├── minigames_server.py           # Servidor WebSocket
├── minigames_pygame.py           # Minijuegos nativos
└── minigames_web/                # Minijuegos web
    ├── index.html                # Página principal
    ├── style.css                 # Estilos profesionales
    ├── eyeTracking.js            # Cliente WebSocket
    ├── games.js                  # Lógica de juegos
    └── main.js                   # Controlador principal
```

## 🎨 Personalización

### Colores
Todos los archivos usan el mismo esquema de colores. Para cambiar:

**Python (pygame)**:
```python
COLOR_PRIMARY = (45, 85, 255)    # Azul principal
COLOR_SUCCESS = (34, 197, 94)    # Verde
COLOR_DANGER = (239, 68, 68)     # Rojo
```

**Web (CSS)**:
```css
--color-primary: #2d55ff;
--color-success: #22c55e;
--color-danger: #ef4444;
```

### Agregar Nuevos Juegos

#### En Web (games.js):
```javascript
class MyNewGame extends Game {
    constructor(canvas) {
        super(canvas, 'Mi Juego');
        // Tu código
    }
    // Implementa update() y draw()
}

// Registra el juego
games['myNewGame'] = MyNewGame;
```

#### En Pygame (minigames_pygame.py):
```python
class MyPygameGame(MiniGame):
    def __init__(self, gestures):
        super().__init__("Mi Juego", gestures)
        # Tu código
    
    def update(self, gaze_point, fixation):
        # Lógica del juego
    
    def draw(self, screen):
        # Renderizado
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Ideas para nuevos juegos:
- 🐍 Snake con control de mirada
- ⚡ Test de reacción
- 🎨 Aplicación de dibujo
- 📊 Visualización de datos de eye-tracking

## 📄 Licencia

Mismo que el proyecto principal EyeGestures.

## ✨ Créditos

- EyeGestures por NativeSensors
- Interfaz profesional diseñada con pygame y tecnologías web modernas
- Minijuegos implementados con eye-tracking en tiempo real

---

**¡Disfruta de los minijuegos con eye-tracking! 👁️🎮**
