# 👁️ EyeGestures Android - Control de Juegos con Seguimiento Ocular# 👁️ EyeGestures Android - Control de Juegos con Seguimiento Ocular# Eye Gestures Android con ML Kit



Aplicación Android nativa que permite controlar juegos usando únicamente los movimientos de los ojos. Utiliza **ML Kit Face Detection** con **algoritmo basado en el proyecto web original**.



---Aplicación Android nativa que permite controlar juegos usando únicamente los movimientos de los ojos. Utiliza **ML Kit Face Detection** para rastrear la mirada del usuario en tiempo real.Implementación nativa de Eye Gestures para Android usando ML Kit Face Detection y CameraX.



## 🎯 Características Principales



### ✨ Sistema de Calibración Avanzado---## 🎯 Características

- **13 puntos de calibración óptimos** (4 esquinas + 4 bordes + 4 cruz + 1 centro)

- **Validación robusta** - No avanza sin detectar el rostro correctamente

- **Feedback visual en tiempo real**:

  - Cuenta regresiva de 2 segundos por punto## 🎯 Características Principales- ✅ Detección de parpadeos usando probabilidad de ojos abiertos

  - Indicador de detección de rostro ("✓ Rostro detectado" / "⚠ Buscando rostro...")

  - Barra de progreso durante la captura- ✅ Detección de dirección de la mirada usando ángulos de rotación de la cabeza

  - Pantalla de error con opción de reintentar

- **Duración total**: ~26 segundos (vs 50 segundos con 25 puntos)### ✨ Sistema de Calibración Avanzado- ✅ Integración con Jetpack Compose



### 🎮 Juegos Incluidos- **13 puntos de calibración óptimos** (4 esquinas + 4 bordes + 4 cruz + 1 centro)- ✅ Ejemplo de juego Snake controlado por la mirada



#### 1. **Snake (Serpiente)**- **Validación robusta** - No avanza sin detectar el rostro correctamente- ✅ API simple y fácil de integrar

- Control direccional con la mirada (arriba, abajo, izquierda, derecha)

- Sistema de zonas muertas (30%) para evitar movimientos accidentales- **Feedback visual en tiempo real**:

- Debounce de 150ms para cambios de dirección suaves

- Cursor visual superpuesto que muestra dónde miras  - Cuenta regresiva de 2 segundos por punto## 📋 Requisitos

- Cámara opcional visible para monitorear el seguimiento

  - Indicador de detección de rostro ("✓ Rostro detectado" / "⚠ Buscando rostro...")

#### 2. **Labyrinth (Laberinto)**

- Control direccional con la mirada  - Barra de progreso durante la captura- Android Studio Hedgehog | 2023.1.1 o superior

- Detección de colisiones con paredes

- Sistema de puntuación basado en movimientos  - Pantalla de error con opción de reintentar- minSdk: 24 (Android 7.0)

- Múltiples niveles de dificultad

- Cursor visual y cámara opcional- **Duración total**: ~26 segundos (vs 50 segundos con 25 puntos)- targetSdk: 34 (Android 14)



### 🔧 Tecnología de Seguimiento- **Sensibilidad aumentada**: 12x horizontal, 10x vertical- Kotlin 1.9.0+



#### **IMPORTANTE: Algoritmo Basado en Proyecto Web Original**



Este proyecto replica el algoritmo de `eyegestures.js` del proyecto web, que usa **contornos reales de los ojos**, NO ángulos de Euler de la cabeza.### 🎮 Juegos Incluidos## 🚀 Configuración



- **ML Kit Face Detection** con configuración avanzada:

  - Modo de rendimiento preciso (**PERFORMANCE_MODE_ACCURATE**)

  - **Contornos completos de ojos** (CONTOUR_MODE_ALL) - **CRÍTICO**#### 1. **Snake (Serpiente)****Ver `SETUP.md` para la guía completa de configuración del proyecto.**

  - Landmarks y tracking ID habilitado

  - Tamaño mínimo de rostro: 15% de la imagen- Control direccional con la mirada (arriba, abajo, izquierda, derecha)



- **Algoritmo de seguimiento (REPLICADO DE WEB)**:- Sistema de zonas muertas (30%) para evitar movimientos accidentales### 1. Dependencias (build.gradle.kts)

  ```

  PROYECTO WEB (eyegestures.js):- Debounce de 150ms para cambios de dirección suaves

  - Usa MediaPipe FaceMesh

  - Obtiene contornos completos de ambos ojos (LEFT_EYE_KEYPOINTS, RIGHT_EYE_KEYPOINTS)- Cursor visual superpuesto que muestra dónde miras```kotlin

  - Calcula centro geométrico de cada conjunto de puntos

  - Normaliza respecto a bounding box de la cara- Cámara opcional visible para monitorear el seguimientodependencies {

  - Aplica factores de escala (width/startWidth, height/startHeight)

  - Compensa movimiento de cabeza (head_starting_pos)    // Jetpack Compose

  

  PROYECTO ANDROID (FaceAnalyzer.kt):#### 2. **Labyrinth (Laberinto)**    implementation(platform("androidx.compose:compose-bom:2024.02.00"))

  ✅ Usa ML Kit Face Detection con CONTOUR_MODE_ALL

  ✅ Obtiene FaceContour.LEFT_EYE y FaceContour.RIGHT_EYE (equivalente a keypoints web)- Control direccional con la mirada    implementation("androidx.compose.ui:ui")

  ✅ Calcula centro geométrico de cada conjunto de puntos

  ✅ Normaliza respecto a bounding box de todos los landmarks- Detección de colisiones con paredes    implementation("androidx.compose.material3:material3")

  ✅ Aplica factores de escala (width/startWidth, height/startHeight)

  ✅ Compensa movimiento de cabeza (headStartingPos)- Sistema de puntuación basado en movimientos    implementation("androidx.compose.material:material-icons-extended")

  ✅ Buffer de suavizado de 20 frames (igual que web)

  ❌ NO usa ángulos Euler (movimiento de cabeza)- Múltiples niveles de dificultad    

  ⚠️  Fallback a Euler solo si contornos no disponibles

  ```- Cursor visual y cámara opcional    // CameraX



- **Diferencia clave con versión anterior**:    val cameraxVersion = "1.3.1"

  - ❌ **VERSIÓN ANTERIOR (INCORRECTA)**: Usaba `headEulerAngleY/X` → detectaba movimiento de CABEZA, no de OJOS

  - ✅ **VERSIÓN ACTUAL (CORRECTA)**: Usa contornos de ojos → detecta movimiento REAL de OJOS### 🔧 Tecnología de Seguimiento    implementation("androidx.camera:camera-core:$cameraxVersion")



- **Proceso de detección**:    implementation("androidx.camera:camera-camera2:$cameraxVersion")

  1. Obtener contornos LEFT_EYE y RIGHT_EYE (lista de puntos)

  2. Calcular bounding box de toda la cara (min/max X/Y)- **ML Kit Face Detection** con configuración avanzada:    implementation("androidx.camera:camera-lifecycle:$cameraxVersion")

  3. Normalizar coordenadas de ojos: `((punto - offset) / width) * scaleX`

  4. Calcular centro de cada ojo (promedio de puntos)  - Modo de rendimiento rápido (PERFORMANCE_MODE_FAST)    implementation("androidx.camera:camera-view:$cameraxVersion")

  5. Calcular centro entre ambos ojos (posición de mirada base)

  6. Compensar movimiento de cabeza (headStartingPos)  - Landmarks y contornos de ojos completos    

  7. Aplicar suavizado (solo en juegos)

  - Tracking ID habilitado para seguimiento fluido    // ML Kit Face Detection

- **Suavizado condicional**:

  - **Durante calibración**: `enableSmoothing = false` (posiciones exactas)  - Tamaño mínimo de rostro: 15% de la imagen    implementation("com.google.mlkit:face-detection:16.1.6")

  - **Durante juego**: `enableSmoothing = true` (movimientos fluidos, buffer de 20 frames)

    

- **Seguimiento continuo**:

  - Cámara invisible de fondo siempre activa- **Algoritmo de seguimiento**:    // Coroutines

  - Independiente de la visibilidad de la vista previa

  - Garantiza tracking ininterrumpido después de calibración  - Usa ángulos de Euler de la cabeza (headEulerAngleY/X) como proxy de la mirada    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")



---  - Landmarks de ojos (LEFT_EYE, RIGHT_EYE) para posición precisa}



## 📋 Requisitos del Sistema  - Rastreo de escala de cabeza para compensar acercamiento/alejamiento```



### Hardware  - Buffer de suavizado de 20 frames (solo en juegos, no en calibración)

- **Android 7.0 (API 24)** o superior

- **Cámara frontal** obligatoria### 2. Permisos (AndroidManifest.xml)

- **RAM**: Mínimo 2GB recomendado

- **Procesador**: ARM (armeabi-v7a, arm64-v8a) o x86/x86_64- **Suavizado condicional**:



### Software  - **Durante calibración**: Suavizado desactivado (posiciones exactas)```xml

- Android SDK 35

- Gradle 9.0+  - **Durante juego**: Suavizado activado (movimientos fluidos)<!-- Permiso para usar la cámara -->

- Kotlin 1.9+

- Java 8+<uses-permission android:name="android.permission.CAMERA" />



---- **Seguimiento continuo**:



## 🚀 Instalación y Compilación  - Cámara invisible de fondo siempre activa<!-- Declarar que la app requiere cámara frontal -->



### 1. Clonar el Repositorio  - Independiente de la visibilidad de la vista previa<uses-feature 

```bash

git clone <repository-url>  - Garantiza tracking ininterrumpido después de calibración    android:name="android.hardware.camera.front" 

cd EyeGesturesLite/android

```    android:required="true" />



### 2. Compilar el APK---

```bash

# En Windows (PowerShell)<!-- ML Kit Face Detection -->

.\gradlew.bat assembleDebug

## 📋 Requisitos del Sistema<application>

# En Linux/Mac

./gradlew assembleDebug    <meta-data

```

### Hardware        android:name="com.google.mlkit.vision.DEPENDENCIES"

El APK se generará en:

```- **Android 7.0 (API 24)** o superior        android:value="face" />

android/app/build/outputs/apk/debug/app-debug.apk

```- **Cámara frontal** obligatoria</application>



### 3. Instalar en Dispositivo- **RAM**: Mínimo 2GB recomendado```

```bash

# Conectar dispositivo Android por USB (habilitar depuración USB)- **Procesador**: ARM (armeabi-v7a, arm64-v8a) o x86/x86_64

adb install app/build/outputs/apk/debug/app-debug.apk

### 3. Solicitud de Permisos en Runtime

# O instalar manualmente copiando el APK al dispositivo

```### Software



---- Android SDK 35La app solicita automáticamente el permiso de cámara al iniciar. Ver `MainActivity.kt` para la implementación completa.



## 🏗️ Arquitectura del Proyecto- Gradle 9.0+



### Estructura de Directorios- Kotlin 1.9+### 3. Estructura de archivos

```

android/- Java 8+

├── app/

│   ├── build.gradle.kts          # Configuración de dependencias```

│   └── src/main/

│       ├── AndroidManifest.xml   # Permisos y configuración---android/

│       └── java/com/example/eyegestures/

│           ├── MainActivity.kt              # Activity principal├── MainActivity.kt              # Activity principal con Compose

│           ├── MenuScreen.kt                # Pantalla de menú

│           ├── CalibrationScreen.kt         # UI de calibración## 🚀 Instalación y Compilación├── CameraPreviewView.kt         # Configuración de CameraX

│           ├── CalibrationViewModel.kt      # Lógica de calibración

│           ├── CalibrationManager.kt        # Mapeo pupila → pantalla├── FaceAnalyzer.kt              # Análisis de rostros con ML Kit

│           ├── SnakeScreen.kt               # Juego Snake

│           ├── SnakeViewModel.kt            # Lógica del Snake### 1. Clonar el Repositorio├── BlinkDetector.kt             # Lógica de detección de parpadeos

│           ├── LabyrinthScreen.kt           # Juego Laberinto

│           ├── MazeViewModel.kt             # Lógica del Laberinto```bash├── GazeDirectionDetector.kt     # Lógica de dirección de mirada

│           ├── CameraPreviewView.kt         # Vista de cámara

│           ├── FaceAnalyzer.kt              # ⭐ DETECCIÓN DE MIRADA (algoritmo web)git clone <repository-url>├── SnakeGameExample.kt          # Ejemplo de integración con juego

│           ├── GazeCursor.kt                # Cursor visual de mirada

│           ├── PupilTrackingController.kt   # Conversión mirada → direccionescd EyeGesturesLite/android└── build.gradle.kts             # Dependencias del proyecto

│           ├── SmoothingBuffer.kt           # Buffer de suavizado

│           ├── GameDirection.kt             # Enum de direcciones``````

│           └── DiagnosticWindow.kt          # Ventana de diagnóstico

└── build.gradle.kts              # Configuración raíz

```

### 2. Compilar el APK## 🔧 Uso

### Componentes Clave

```bash

#### 1. **FaceAnalyzer** (`FaceAnalyzer.kt`) ⭐ COMPONENTE CRÍTICO

# En Windows (PowerShell)### Detección de Parpadeos

**REPLICACIÓN DEL ALGORITMO WEB**

.\gradlew.bat assembleDebug

Analiza frames de la cámara usando ML Kit Face Detection con el mismo algoritmo que `eyegestures.js`.

```kotlin

**Código web original (JavaScript)**:

```javascript# En Linux/Macval blinkDetector = BlinkDetector(

// eyegestures.js - líneas 257-350

const LEFT_EYE_KEYPOINTS = [33, 133, 160, 159, 158, ...];./gradlew assembleDebug    onBlinkDetected = {

const RIGHT_EYE_KEYPOINTS = [362, 263, 387, 386, 385, ...];

```        println("¡Parpadeo detectado!")

let l_landmarks = LEFT_EYE_KEYPOINTS.map(index => landmarks[index]);

let r_landmarks = RIGHT_EYE_KEYPOINTS.map(index => landmarks[index]);    }



// Normalizar coordenadasEl APK se generará en:)

left_eye_coordinates.push([

    (((landmark.x - offset_x) / width) * scale_x),```

    (((landmark.y - offset_y) / height) * scale_y)

]);android/app/build/outputs/apk/debug/app-debug.apk// En el análisis de cada frame



// Calcular posición de mirada```blinkDetector.analyze(leftEyeOpenProbability, rightEyeOpenProbability)

let point = this.calibrator.predict(keypoints);

``````



**Código Android equivalente (Kotlin)**:### 3. Instalar en Dispositivo

```kotlin

// FaceAnalyzer.kt```bash**Cómo funciona:**

val leftEyeContour = face.getContour(FaceContour.LEFT_EYE)

val rightEyeContour = face.getContour(FaceContour.RIGHT_EYE)# Conectar dispositivo Android por USB (habilitar depuración USB)1. ML Kit proporciona `leftEyeOpenProbability` y `rightEyeOpenProbability` (0.0 a 1.0)



val leftEyePoints = leftEyeContour.pointsadb install app/build/outputs/apk/debug/app-debug.apk2. Si ambos valores bajan de 0.3 → ojos cerrados

val rightEyePoints = rightEyeContour.points

3. Si después vuelven a subir por encima de 0.5 → parpadeo detectado

// Normalizar coordenadas (igual que web)

val leftEyeCoordinates = leftEyePoints.map { point -># O instalar manualmente copiando el APK al dispositivo4. Incluye debounce de 300ms para evitar detecciones duplicadas

    PointF(

        ((point.x - offsetX) / width) * scaleX,```

        ((point.y - offsetY) / height) * scaleY

    )### Detección de Dirección de Mirada

}

---

// Calcular centro de ojos

val leftEyeCenter = calculateCenter(leftEyeCoordinates)```kotlin

val rightEyeCenter = calculateCenter(rightEyeCoordinates)

## 🏗️ Arquitectura del Proyectoval gazeDetector = GazeDirectionDetector(

val gazeCenterX = (leftEyeCenter.x + rightEyeCenter.x) / 2f

val gazeCenterY = (leftEyeCenter.y + rightEyeCenter.y) / 2f    onGazeDirectionChanged = { direction ->

```

### Estructura de Directorios        when (direction) {

**Características**:

- ✅ Detección de rostro en tiempo real```            "Izquierda" -> // Usuario mira a la izquierda

- ✅ Obtiene **contornos completos de ojos** (no solo landmarks básicos)

- ✅ Calcula centro geométrico de puntos de contornoandroid/            "Derecha" -> // Usuario mira a la derecha

- ✅ Normaliza coordenadas respecto a bounding box

- ✅ Aplica factores de escala (compensa distancia)├── app/            "Arriba" -> // Usuario mira hacia arriba

- ✅ Compensa movimiento de cabeza

- ✅ Suavizado opcional con buffer de 20 frames│   ├── build.gradle.kts          # Configuración de dependencias            "Abajo" -> // Usuario mira hacia abajo

- ❌ NO usa ángulos Euler (headEulerAngleY/X)

│   └── src/main/            "Centro" -> // Usuario mira al frente

**Parámetros**:

```kotlin│       ├── AndroidManifest.xml   # Permisos y configuración        }

FaceAnalyzer(

    enableSmoothing = true,  // true para juegos, false para calibración│       └── java/com/example/eyegestures/    }

    onPupilPositionDetected = { pupilX, pupilY ->

        // Callback con posición de mirada│           ├── MainActivity.kt              # Activity principal)

    },

    onFaceDetected = { detected ->│           ├── MenuScreen.kt                # Pantalla de menú

        // Callback para saber si hay rostro en frame

    }│           ├── CalibrationScreen.kt         # UI de calibración// En el análisis de cada frame

)

```│           ├── CalibrationViewModel.kt      # Lógica de calibracióngazeDetector.analyze(headEulerAngleY, headEulerAngleX, headEulerAngleZ)



**Modo Fallback**:│           ├── CalibrationManager.kt        # Mapeo pupila → pantalla```

Si los contornos no están disponibles (dispositivos antiguos), usa:

- Landmarks básicos LEFT_EYE y RIGHT_EYE│           ├── SnakeScreen.kt               # Juego Snake

- Ángulos Euler como aproximación (menos preciso)

- Log de advertencia: "Using fallback mode (Euler angles) - less accurate"│           ├── SnakeViewModel.kt            # Lógica del Snake**Ángulos de Euler explicados:**



#### 2. **CalibrationManager** (`CalibrationManager.kt`)│           ├── LabyrinthScreen.kt           # Juego Laberinto- `headEulerAngleY`: Rotación horizontal

Gestiona el proceso de calibración y mapeo.

│           ├── MazeViewModel.kt             # Lógica del Laberinto  - Negativo = izquierda

**Funciones principales**:

- `addCalibrationPoint(pupilX, pupilY, screenX, screenY)`: Añade punto de calibración│           ├── CameraPreviewView.kt         # Vista de cámara  - Positivo = derecha

- `finishCalibration()`: Completa calibración

- `mapToScreen(pupilX, pupilY): PointF`: Convierte posición pupila → pantalla│           ├── FaceAnalyzer.kt              # Detección de rostro ML Kit  - ~0 = frente

- `isCalibrated: Boolean`: Estado de calibración

│           ├── GazeCursor.kt                # Cursor visual de mirada- `headEulerAngleX`: Inclinación vertical

**Algoritmo de mapeo**:

- Usa interpolación ponderada por distancia inversa (IDW)│           ├── PupilTrackingController.kt   # Conversión mirada → direcciones  - Negativo = arriba

- Busca los 4 puntos de calibración más cercanos

- Calcula posición en pantalla basado en vecinos│           ├── SmoothingBuffer.kt           # Buffer de suavizado  - Positivo = abajo



#### 3. **CalibrationViewModel** (`CalibrationViewModel.kt`)│           ├── GameDirection.kt             # Enum de direcciones  - ~0 = frente

Lógica de negocio de la calibración.

│           └── DiagnosticWindow.kt          # Ventana de diagnóstico- `headEulerAngleZ`: Inclinación lateral

**Estados**:

```kotlin└── build.gradle.kts              # Configuración raíz

sealed class CalibrationState {

    object Idle                                           // Esperando inicio```**Umbrales:**

    data class Calibrating(hasValidData: Boolean)        // En proceso

    data class DetectionError(currentPoint: Int, message: String)  // Error- 15° para movimiento horizontal

    data class Completed(calibratedPoints: List<CalibrationPoint>) // Completado

}### Componentes Clave- 15° para movimiento vertical

```

- Debounce de 200ms

**Validaciones**:

- Verifica que `pupilPos != null` antes de capturar#### 1. **FaceAnalyzer** (`FaceAnalyzer.kt`)

- Valida rango de coordenadas de pupila

- No avanza al siguiente punto sin datos válidosAnaliza frames de la cámara usando ML Kit Face Detection.### Integración con Compose

- Permite reintentar puntos con error



#### 4. **GazeCursorManager** (`GazeCursor.kt`)

Singleton que gestiona el cursor de mirada globalmente.**Características:**```kotlin



**API**:- Detección de rostro en tiempo real@Composable

```kotlin

// Actualizar posición- Calcula posición de pupila usando:fun MyScreen() {

GazeCursorManager.updateGazePosition(screenX, screenY)

  - Ángulos de Euler de la cabeza (headEulerAngleY/X)    var blinkDetected by remember { mutableStateOf(false) }

// Marcar calibración completada

GazeCursorManager.setCalibrated(true)  - Landmarks de ojos (LEFT_EYE, RIGHT_EYE)    var gazeDirection by remember { mutableStateOf("Centro") }



// Obtener estado  - Factor de escala de cabeza    

GazeCursorManager.isCalibrated(): Boolean

- Suavizado opcional con buffer de 20 frames    CameraPreviewView(

// Observar posición (StateFlow)

GazeCursorManager.gazePosition: StateFlow<Offset>- Sensibilidad: 12x horizontal, 10x vertical        onBlinkDetected = { blinkDetected = true },

```

        onGazeDirectionChanged = { direction -> gazeDirection = direction },

#### 5. **PupilTrackingController** (`PupilTrackingController.kt`)

Convierte posición de mirada en direcciones de juego.**Parámetros:**        onEyeOpenProbabilityChanged = { left, right ->



**Características**:```kotlin            // Opcional: usar los valores en bruto

- Grid 3×3 (9 zonas)

- Zona muerta central del 30% (evita movimientos accidentales)FaceAnalyzer(        }

- Debounce de 150ms entre cambios de dirección

- Mapeo: zonas → GameDirection (UP, DOWN, LEFT, RIGHT, CENTER)    enableSmoothing = true,  // true para juegos, false para calibración    )



**Uso**:    onPupilPositionDetected = { pupilX, pupilY ->}

```kotlin

val controller = PupilTrackingController(        // Callback con posición de pupila```

    screenWidth = 1080f,

    screenHeight = 1920f    }

)

)### Para Juegos (Snake)

controller.updatePupilPosition(pupilX, pupilY)

val direction = controller.getDirection()  // UP, DOWN, LEFT, RIGHT, CENTER```

```

```kotlin

#### 6. **SmoothingBuffer** (`SmoothingBuffer.kt`)

Buffer circular para suavizado de coordenadas.#### 2. **CalibrationManager** (`CalibrationManager.kt`)val gazeDetector = GazeDirectionDetector { }



**Características**:Gestiona el proceso de calibración y mapeo.

- Tamaño: 20 posiciones (igual que web)

- Calcula promedio móvil// Obtener dirección específica para juegos

- Solo se usa en juegos (no en calibración)

**Funciones principales:**val gameDirection = gazeDetector.getGameDirection(

---

- `addCalibrationPoint(pupilX, pupilY, screenX, screenY)`: Añade punto de calibración    angleY = headEulerAngleY,

## 🎨 Flujo de Usuario

- `finishCalibration()`: Completa calibración    angleX = headEulerAngleX

### 1️⃣ Inicio de la App

```- `mapToScreen(pupilX, pupilY): PointF`: Convierte posición pupila → pantalla)

MainActivity → Solicitud de Permiso de Cámara

              ↓- `isCalibrated: Boolean`: Estado de calibración

          MenuScreen (Menú Principal)

```when (gameDirection) {



### 2️⃣ Calibración (Primera Vez)**Algoritmo de mapeo:**    GameDirection.UP -> moveSnakeUp()

```

MenuScreen → Botón "Calibrar"- Usa interpolación ponderada por distancia inversa (IDW)    GameDirection.DOWN -> moveSnakeDown()

             ↓

    CalibrationScreen- Busca los 4 puntos de calibración más cercanos    GameDirection.LEFT -> moveSnakeLeft()

             ↓

    13 Puntos de Calibración- Calcula posición en pantalla basado en vecinos    GameDirection.RIGHT -> moveSnakeRight()

    (Cuenta regresiva 2s cada uno)

             ↓    GameDirection.NONE -> // Sin movimiento

    Validación de Rostro

    - ✓ Detectado: Captura punto#### 3. **CalibrationViewModel** (`CalibrationViewModel.kt`)}

    - ✗ No detectado: Muestra error → Reintentar

             ↓Lógica de negocio de la calibración.```

    Calibración Completada ✅

             ↓

    Volver al Menú

```**Estados:**## 🎮 Juegos de Ejemplo



### 3️⃣ Jugar (Después de Calibrar)```kotlin

```

MenuScreen → Seleccionar Juego (Snake/Labyrinth)sealed class CalibrationState {### 🐍 Snake Game

             ↓

    GameScreen    object Idle                                           // Esperando inicioVer `SnakeGame.kt` y `SnakeGameScreen.kt` para una implementación completa de Snake controlado por la mirada.

    - Cámara invisible de fondo (siempre activa)

    - Cámara visible opcional (toggle con icono)    data class Calibrating(hasValidData: Boolean)        // En proceso

    - Cursor de mirada superpuesto (verde)

    - Control con MIRADA (no con cabeza)    data class DetectionError(currentPoint: Int, message: String)  // Error**Archivos del Juego:**

             ↓

    Jugar Normalmente    data class Completed(calibratedPoints: List<CalibrationPoint>) // Completado- **SnakeGame.kt**: Lógica del juego (traducido desde JavaScript)

    - Mirar arriba → Mover arriba

    - Mirar abajo → Mover abajo}  - Data classes: `GridPosition`, `Direction`, `GameState`

    - Mirar izquierda → Mover izquierda

    - Mirar derecha → Mover derecha```  - Método `updateGame()`: Actualiza el estado del juego

```

  - Método `checkSelfCollision()`: Verifica colisiones

---

**Validaciones:**  - Método `updateDirectionFromGaze()`: Integración con ML Kit

## 🔑 Permisos Requeridos

- Verifica que `pupilPos != null` antes de capturar  

### AndroidManifest.xml

```xml- Valida rango de coordenadas de pupila- **SnakeGameScreen.kt**: UI con Jetpack Compose

<!-- Permiso para usar la cámara -->

<uses-permission android:name="android.permission.CAMERA" />- No avanza al siguiente punto sin datos válidos  - Canvas personalizado con efectos visuales



<!-- Declarar que la app requiere cámara frontal -->- Permite reintentar puntos con error  - Integración completa con CameraX y Eye Gestures

<uses-feature 

    android:name="android.hardware.camera.front"   - Game loop con coroutines

    android:required="true" />

#### 4. **GazeCursorManager** (`GazeCursor.kt`)

<!-- ML Kit Face Detection - descarga automática -->

<meta-dataSingleton que gestiona el cursor de mirada globalmente.**Características:**

    android:name="com.google.mlkit.vision.DEPENDENCIES"

    android:value="face" />- ✅ Control con movimiento de cabeza (4 direcciones)

```

**API:**- ✅ Parpadeo para pausar/reiniciar

### Solicitud en Tiempo de Ejecución

La app solicita el permiso de cámara al iniciar. Si se deniega, muestra una pantalla explicando por qué es necesario el permiso.```kotlin- ✅ Vista de cámara en tiempo real



---// Actualizar posición- ✅ Puntuación y feedback visual



## 📦 Dependencias PrincipalesGazeCursorManager.updateGazePosition(screenX, screenY)- ✅ Efectos visuales (grid, pulso en comida, gradiente en serpiente)



### Jetpack Compose (UI)- ✅ Indicador de mirada en tiempo real

```kotlin

implementation("androidx.compose:compose-bom:2024.02.00")// Marcar calibración completada- ✅ Wrap-around en bordes (teletransporte)

implementation("androidx.compose.ui:ui")

implementation("androidx.compose.material3:material3")GazeCursorManager.setCalibrated(true)

implementation("androidx.compose.material:material-icons-extended")

```### 🧩 Maze Game (Laberinto)



### CameraX (Captura de Video)// Obtener estadoVer `MazeGame.kt` y `MazeGameScreen.kt` para un juego de laberinto completo.

```kotlin

val cameraxVersion = "1.3.1"GazeCursorManager.isCalibrated(): Boolean

implementation("androidx.camera:camera-core:$cameraxVersion")

implementation("androidx.camera:camera-camera2:$cameraxVersion")**Archivos del Juego:**

implementation("androidx.camera:camera-lifecycle:$cameraxVersion")

implementation("androidx.camera:camera-view:$cameraxVersion")// Observar posición (StateFlow)- **MazeGame.kt**: Lógica del juego

```

GazeCursorManager.gazePosition: StateFlow<Offset>  - Data classes: `GridPosition`, `MazeGameState`, `CellType`

### ML Kit (Face Detection)

```kotlin```  - Generación aleatoria de laberinto 10x10

implementation("com.google.mlkit:face-detection:16.1.6")

```  - Sistema de puntuación basado en eficiencia



### Coroutines (Asincronía)#### 5. **PupilTrackingController** (`PupilTrackingController.kt`)  - Detección automática de victoria

```kotlin

implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")Convierte posición de mirada en direcciones de juego.  

```

- **MazeGameScreen.kt**: UI con Jetpack Compose

### Navigation Compose

```kotlin**Características:**  - Cuadrícula 10x10 con Canvas personalizado

implementation("androidx.navigation:navigation-compose:2.7.7")

```- Grid 3×3 (9 zonas)  - Jugador (círculo azul con cara 😊)



---- Zona muerta central del 30% (evita movimientos accidentales)  - Meta (estrella dorada pulsante ⭐)



## 🛠️ Configuración de Desarrollo- Debounce de 150ms entre cambios de dirección  - 4 botones direccionales grandes (80dp)



### Android Studio- Mapeo: zonas → GameDirection (UP, DOWN, LEFT, RIGHT, CENTER)  - Controles por mirada integrados

1. Abrir Android Studio

2. **File → Open** → Seleccionar carpeta `android/`

3. Esperar sincronización de Gradle

4. Conectar dispositivo Android o iniciar emulador**Uso:****Características:**

5. **Run → Run 'app'**

```kotlin- ✅ Cuadrícula 10x10 dibujada con Canvas

### Gradle

```kotlinval controller = PupilTrackingController(- ✅ Jugador animado con cara sonriente

compileSdk = 35

minSdk = 24    screenWidth = 1080f,- ✅ Meta con efecto pulsante

targetSdk = 35

    screenHeight = 1920f- ✅ Paredes con efecto 3D

kotlinCompilerExtensionVersion = "1.5.1"

```)- ✅ Rastro visual del camino recorrido



### Arquitecturas Soportadas- ✅ 4 botones direccionales circulares grandes

```kotlin

ndk {controller.updatePupilPosition(pupilX, pupilY)- ✅ Control por mirada con ML Kit

    abiFilters += listOf("armeabi-v7a", "arm64-v8a", "x86", "x86_64")

}val direction = controller.getDirection()  // UP, DOWN, LEFT, RIGHT, CENTER- ✅ Generación aleatoria de laberinto

```

```- ✅ Sistema de puntuación inteligente

---

- ✅ Overlay de victoria con estadísticas

## 🐛 Depuración y Diagnóstico

#### 6. **SmoothingBuffer** (`SmoothingBuffer.kt`)

### Logs de ML Kit

```kotlinBuffer circular para suavizado de coordenadas.Ver `MAZE_GAME.md` para documentación detallada del juego de laberinto.

// Ver logs en Logcat

Log.d("FaceAnalyzer", "Gaze position: ($pupilX, $pupilY)")

Log.d("CalibrationManager", "Mapped screen position: ($screenX, $screenY)")

```**Características:**## ⚙️ Configuración Avanzada



### Ventana de Diagnóstico- Tamaño: 20 posiciones

La app incluye `DiagnosticWindow.kt` para mostrar información de debug en tiempo real:

- Posición actual de la mirada- Calcula promedio móvil### Ajustar sensibilidad de parpadeo

- Posición del cursor en pantalla

- Estado de calibración- Solo se usa en juegos (no en calibración)

- FPS de detección

```kotlin

### Problemas Comunes

---class BlinkDetector {

#### 1. **"No se detectó tu rostro"**

- **Causa**: Poca iluminación o rostro fuera de cámara    companion object {

- **Solución**: Asegurar buena iluminación y mirar directamente a la cámara

## 🎨 Flujo de Usuario        private const val EYE_CLOSED_THRESHOLD = 0.3f  // Más bajo = más sensible

#### 2. **Cursor se mueve con movimiento de cabeza en lugar de ojos**

- **Causa**: Usando versión anterior con Euler angles        private const val EYE_OPEN_THRESHOLD = 0.5f    // Más bajo = más sensible

- **Solución**: ✅ SOLUCIONADO - Nueva versión usa contornos de ojos reales

### 1️⃣ Inicio de la App    }

#### 3. **Cursor no se mueve después de calibrar**

- **Causa**: Cámara no activa```}

- **Solución**: ✅ SOLUCIONADO - Cámara invisible de fondo siempre activa

MainActivity → Solicitud de Permiso de Cámara```

#### 4. **"Using fallback mode (Euler angles)"** en logs

- **Causa**: Contornos de ojos no disponibles (dispositivo antiguo)              ↓

- **Solución**: Normal, funcionará pero menos preciso. Considerar actualizar dispositivo.

          MenuScreen (Menú Principal)### Ajustar sensibilidad de dirección

#### 5. **Movimientos bruscos del cursor**

- **Causa**: Suavizado desactivado o buffer pequeño```

- **Solución**: Verificar que `enableSmoothing = true` en juegos

```kotlin

#### 6. **Calibración imprecisa**

- **Causa**: Movimiento de cabeza durante calibración### 2️⃣ Calibración (Primera Vez)class GazeDirectionDetector {

- **Solución**: Mantener cabeza quieta, solo mover ojos

```    companion object {

---

MenuScreen → Botón "Calibrar"        private const val HORIZONTAL_THRESHOLD = 15f  // Más bajo = más sensible

## 📊 Comparación: Proyecto Web vs Android

             ↓        private const val VERTICAL_THRESHOLD = 15f    // Más bajo = más sensible

| Característica | Proyecto Web | Proyecto Android |

|----------------|--------------|------------------|    CalibrationScreen    }

| **Framework ML** | MediaPipe FaceMesh | ML Kit Face Detection |

| **Detección de ojos** | Keypoints 468, 473 + contornos | FaceContour.LEFT_EYE, RIGHT_EYE |             ↓}

| **Algoritmo** | Centro geométrico de contornos | ✅ **Igual** - Centro geométrico |

| **Normalización** | `(x - offset) / width * scale` | ✅ **Igual** - Misma fórmula |    13 Puntos de Calibración```

| **Compensación cabeza** | `head_starting_pos` | ✅ **Igual** - `headStartingPos` |

| **Buffer suavizado** | 20 frames | ✅ **Igual** - 20 frames |    (Cuenta regresiva 2s cada uno)

| **Calibración** | 25 puntos | ✅ Mejorado - 13 puntos óptimos |

| **Usa Euler angles** | ❌ NO | ❌ **NO** (solo fallback) |             ↓### Umbral personalizado

| **Precisión** | Alta (MediaPipe) | Alta (ML Kit con contornos) |

    Validación de Rostro

---

    - ✓ Detectado: Captura punto```kotlin

## 🚧 Desarrollo Futuro

    - ✗ No detectado: Muestra error → Reintentarval direction = gazeDetector.analyzeWithCustomThresholds(

### Posibles Mejoras

- [ ] Soporte para OpenCV (aún más precisión)             ↓    headEulerAngleY = angleY,

- [ ] Calibración adaptativa (recalibración automática)

- [ ] Más juegos (Pong, Target Practice, Collect)    Calibración Completada ✅    headEulerAngleX = angleX,

- [ ] Modo de entrenamiento

- [ ] Estadísticas de precisión             ↓    horizontalThreshold = 10f,  // Más sensible

- [ ] Guardado de perfiles de calibración

- [ ] Soporte para tablets    Volver al Menú    verticalThreshold = 20f     // Menos sensible

- [ ] Modo oscuro

```)

### Optimizaciones de Rendimiento

- [ ] Reducir latencia de detección (< 50ms)```

- [ ] Optimizar consumo de batería

- [ ] Modo de ahorro de energía### 3️⃣ Jugar (Después de Calibrar)

- [ ] Cache de calibración en SharedPreferences

```## 🔍 ML Kit Face Detection - Opciones

---

MenuScreen → Seleccionar Juego (Snake/Labyrinth)

## 📝 Historial de Cambios

             ↓```kotlin

### Versión 1.1 (Octubre 2025) - **CORRECCIÓN CRÍTICA**

- ✅ **CORREGIDO**: Algoritmo ahora usa contornos REALES de ojos (FaceContour)    GameScreenval options = FaceDetectorOptions.Builder()

- ✅ **CORREGIDO**: NO depende de ángulos Euler (movimiento de cabeza)

- ✅ Replicación exacta del algoritmo del proyecto web    - Cámara invisible de fondo (siempre activa)    .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)

- ✅ Fallback a Euler angles solo si contornos no disponibles

- ✅ Mayor precisión en detección de mirada    - Cámara visible opcional (toggle con icono)    .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_ALL)



### Versión 1.0 (Octubre 2025)    - Cursor de mirada superpuesto (verde)    .setMinFaceSize(0.15f)

- ✅ Calibración optimizada (13 puntos, 26 segundos)

- ✅ Validación robusta con retry    - Control con la mirada    .enableTracking()

- ✅ Feedback visual en tiempo real

- ✅ Suavizado condicional             ↓    .build()

- ✅ Seguimiento continuo (cámara invisible)

- ✅ Cursor visible en todos los juegos    Jugar Normalmente```

- ❌ **BUG**: Usaba Euler angles (movimiento de cabeza, no ojos)

    - Mirar arriba → Mover arriba

---

    - Mirar abajo → Mover abajo**Modos de rendimiento:**

## 📄 Licencia

    - Mirar izquierda → Mover izquierda- `PERFORMANCE_MODE_FAST`: Más rápido, menos preciso (recomendado)

Ver archivo `LICENSE` en la raíz del proyecto.

    - Mirar derecha → Mover derecha- `PERFORMANCE_MODE_ACCURATE`: Más lento, más preciso

---

```

## 👥 Contribuciones

**Clasificación:**

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio---- `CLASSIFICATION_MODE_ALL`: Incluye probabilidades de ojos y sonrisa

2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)

3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)- `CLASSIFICATION_MODE_NONE`: Sin clasificación

4. Push a la rama (`git push origin feature/AmazingFeature`)

5. Abrir un Pull Request## 🔑 Permisos Requeridos



---## 📊 Valores de ML Kit



## 📞 Soporte### AndroidManifest.xml



Para reportar bugs o solicitar features, por favor abrir un issue en el repositorio.```xml| Propiedad | Rango | Descripción |



---<!-- Permiso para usar la cámara -->|-----------|-------|-------------|



## 🎓 Referencias<uses-permission android:name="android.permission.CAMERA" />| `leftEyeOpenProbability` | 0.0 - 1.0 | 1.0 = ojo abierto, 0.0 = ojo cerrado |



- [ML Kit Face Detection](https://developers.google.com/ml-kit/vision/face-detection)| `rightEyeOpenProbability` | 0.0 - 1.0 | 1.0 = ojo abierto, 0.0 = ojo cerrado |

- [MediaPipe FaceMesh (Web)](https://google.github.io/mediapipe/solutions/face_mesh.html)

- [CameraX Documentation](https://developer.android.com/training/camerax)<!-- Declarar que la app requiere cámara frontal -->| `headEulerAngleY` | -180° a 180° | Rotación horizontal de la cabeza |

- [Jetpack Compose](https://developer.android.com/jetpack/compose)

- [Android Studio](https://developer.android.com/studio)<uses-feature | `headEulerAngleX` | -180° a 180° | Inclinación vertical de la cabeza |

- [Proyecto Web Original](https://github.com/EyeGestures/eyegestures)

    android:name="android.hardware.camera.front" | `headEulerAngleZ` | -180° a 180° | Inclinación lateral de la cabeza |

---

    android:required="true" />

**Versión**: 1.1 (Algoritmo Corregido)  

**Última actualización**: 31 de Octubre 2025  ## 🐛 Solución de Problemas

**Estado**: ✅ Producción (detección basada en contornos REALES de ojos, no movimiento de cabeza)

<!-- ML Kit Face Detection - descarga automática -->

<meta-data### La cámara no se inicia

    android:name="com.google.mlkit.vision.DEPENDENCIES"- Verificar que el permiso CAMERA esté concedido

    android:value="face" />- Verificar que el dispositivo tenga cámara frontal

```- Revisar logs: `adb logcat | grep CameraX`



### Solicitud en Tiempo de Ejecución### Detección de parpadeos muy sensible

La app solicita el permiso de cámara al iniciar. Si se deniega, muestra una pantalla explicando por qué es necesario el permiso.- Aumentar `EYE_CLOSED_THRESHOLD` (ej. 0.4 o 0.5)

- Aumentar `DEBOUNCE_TIME_MS` (ej. 500)

---

### Detección de mirada errática

## 📦 Dependencias Principales- Aumentar `HORIZONTAL_THRESHOLD` y `VERTICAL_THRESHOLD` (ej. 20 o 25)

- Aumentar `DEBOUNCE_TIME_MS`

### Jetpack Compose (UI)

```kotlin### No detecta el rostro

implementation("androidx.compose:compose-bom:2024.02.00")- Ajustar `setMinFaceSize()` (probar 0.1f o 0.2f)

implementation("androidx.compose.ui:ui")- Mejorar iluminación

implementation("androidx.compose.material3:material3")- Asegurar que el rostro está centrado

implementation("androidx.compose.material:material-icons-extended")

```## 📝 Comparación con EyeGesturesLite.js



### CameraX (Captura de Video)| Característica | JavaScript (WebGL) | Kotlin (ML Kit) |

```kotlin|----------------|-------------------|-----------------|

val cameraxVersion = "1.3.1"| Plataforma | Web, navegador | Android nativo |

implementation("androidx.camera:camera-core:$cameraxVersion")| Rendimiento | Moderado | Alto (GPU) |

implementation("androidx.camera:camera-camera2:$cameraxVersion")| Precisión | Buena | Excelente |

implementation("androidx.camera:camera-lifecycle:$cameraxVersion")| Latencia | ~50-100ms | ~20-50ms |

implementation("androidx.camera:camera-view:$cameraxVersion")| Offline | Requiere modelo | Totalmente offline |

```| Batería | Alta | Optimizada |



### ML Kit (Face Detection)## 📄 Licencia

```kotlin

implementation("com.google.mlkit:face-detection:16.1.6")Este código está bajo la misma licencia que EyeGesturesLite.

```

## 🤝 Contribuciones

### Coroutines (Asincronía)

```kotlin¡Las contribuciones son bienvenidas! Por favor abre un issue o pull request.

implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
```

### Navigation Compose
```kotlin
implementation("androidx.navigation:navigation-compose:2.7.7")
```

---

## 🛠️ Configuración de Desarrollo

### Android Studio
1. Abrir Android Studio
2. **File → Open** → Seleccionar carpeta `android/`
3. Esperar sincronización de Gradle
4. Conectar dispositivo Android o iniciar emulador
5. **Run → Run 'app'**

### Gradle
```kotlin
compileSdk = 35
minSdk = 24
targetSdk = 35

kotlinCompilerExtensionVersion = "1.5.1"
```

### Arquitecturas Soportadas
```kotlin
ndk {
    abiFilters += listOf("armeabi-v7a", "arm64-v8a", "x86", "x86_64")
}
```

---

## 🐛 Depuración y Diagnóstico

### Logs de ML Kit
```kotlin
// Ver logs en Logcat
Log.d("FaceAnalyzer", "Pupil position: ($pupilX, $pupilY)")
Log.d("CalibrationManager", "Mapped screen position: ($screenX, $screenY)")
```

### Ventana de Diagnóstico
La app incluye `DiagnosticWindow.kt` para mostrar información de debug en tiempo real:
- Posición actual de la pupila
- Posición del cursor en pantalla
- Estado de calibración
- FPS de detección

### Problemas Comunes

#### 1. **"No se detectó tu rostro"**
- **Causa**: Poca iluminación o rostro fuera de cámara
- **Solución**: Asegurar buena iluminación y mirar directamente a la cámara

#### 2. **Cursor no se mueve después de calibrar**
- **Causa**: Cámara no activa (SOLUCIONADO en última versión)
- **Solución**: Actualizar a última versión con cámara invisible de fondo

#### 3. **Movimientos bruscos del cursor**
- **Causa**: Suavizado desactivado o buffer pequeño
- **Solución**: Verificar que `enableSmoothing = true` en juegos

#### 4. **Calibración imprecisa**
- **Causa**: Movimiento de cabeza durante calibración
- **Solución**: Mantener cabeza quieta, solo mover ojos

---

## 📊 Parámetros de Configuración

### Sensibilidad del Seguimiento
**Ubicación**: `FaceAnalyzer.kt`
```kotlin
val offsetX = eulerY * 12f * scaleX  // Sensibilidad horizontal
val offsetY = eulerX * 10f * scaleY  // Sensibilidad vertical
```

### Buffer de Suavizado
**Ubicación**: `SmoothingBuffer.kt`
```kotlin
private val smoothingBuffer = SmoothingBuffer(maxSize = 20)  // 20 frames
```

### Zona Muerta y Debounce
**Ubicación**: `PupilTrackingController.kt`
```kotlin
val deadZonePercentage = 0.3f  // 30% zona muerta central
val directionDebounceMs = 150L // 150ms entre cambios
```

### Puntos de Calibración
**Ubicación**: `CalibrationScreen.kt`
```kotlin
// 13 puntos óptimos
val calibrationPoints = remember {
    listOf(
        // 4 esquinas
        Offset(0.1f, 0.1f), Offset(0.9f, 0.1f),
        Offset(0.1f, 0.9f), Offset(0.9f, 0.9f),
        // 4 bordes
        Offset(0.5f, 0.1f), Offset(0.5f, 0.9f),
        Offset(0.1f, 0.5f), Offset(0.9f, 0.5f),
        // 4 cruz interna
        Offset(0.3f, 0.3f), Offset(0.7f, 0.3f),
        Offset(0.3f, 0.7f), Offset(0.7f, 0.7f),
        // 1 centro
        Offset(0.5f, 0.5f)
    )
}
```

---

## 🚧 Desarrollo Futuro

### Posibles Mejoras
- [ ] Soporte para OpenCV (más precisión)
- [ ] Calibración adaptativa (recalibración automática)
- [ ] Más juegos (Pong, Target Practice, Collect)
- [ ] Modo de entrenamiento
- [ ] Estadísticas de precisión
- [ ] Guardado de perfiles de calibración
- [ ] Soporte para tablets
- [ ] Modo oscuro

### Optimizaciones de Rendimiento
- [ ] Reducir latencia de detección (< 50ms)
- [ ] Optimizar consumo de batería
- [ ] Modo de ahorro de energía
- [ ] Cache de calibración en SharedPreferences

---

## 📄 Licencia

Ver archivo `LICENSE` en la raíz del proyecto.

---

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

---

## 📞 Soporte

Para reportar bugs o solicitar features, por favor abrir un issue en el repositorio.

---

## 🎓 Referencias

- [ML Kit Face Detection](https://developers.google.com/ml-kit/vision/face-detection)
- [CameraX Documentation](https://developer.android.com/training/camerax)
- [Jetpack Compose](https://developer.android.com/jetpack/compose)
- [Android Studio](https://developer.android.com/studio)

---

**Versión**: 1.0  
**Última actualización**: Octubre 2025  
**Estado**: ✅ Producción (calibración optimizada, seguimiento continuo)
