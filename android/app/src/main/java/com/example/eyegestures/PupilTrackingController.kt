package com.example.eyegestures

import android.graphics.PointF
import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Controlador de Pupil Tracking para juegos
 * 
 * Conecta el sistema de calibración con la lógica de los juegos.
 * Convierte la posición de la pupila calibrada en direcciones de juego.
 * 
 * USO:
 * ```kotlin
 * val pupilController = PupilTrackingController(
 *     screenWidth = 1080,
 *     screenHeight = 1920,
 *     calibrationManager = CalibrationViewModel.getSharedCalibrationManager()
 * )
 * 
 * // Actualizar posición de pupila continuamente
 * pupilController.updatePupilPosition(pupilX, pupilY)
 * 
 * // Observar dirección actual
 * val direction by pupilController.currentDirection.collectAsState()
 * ```
 */
class PupilTrackingController(
    private val screenWidth: Int,
    private val screenHeight: Int,
    private val calibrationManager: CalibrationManager
) {
    // Posición actual en pantalla (después de calibración)
    private val _screenPosition = MutableStateFlow(PointF(screenWidth / 2f, screenHeight / 2f))
    val screenPosition: StateFlow<PointF> = _screenPosition.asStateFlow()
    
    // Dirección actual basada en posición
    private val _currentDirection = MutableStateFlow(GameDirection.NONE)
    val currentDirection: StateFlow<GameDirection> = _currentDirection.asStateFlow()
    
    // Zona de "dead zone" en el centro (% del ancho/alto de pantalla)
    private var deadZone = 0.3f // 30% del centro no genera movimiento
    
    // Dimensiones de la imagen de la cámara (para inversión de eje X)
    private val cameraImageWidth = 480f
    private val cameraImageHeight = 640f
    
    // Control de actualización
    private var lastDirectionChangeTime = 0L
    private val directionDebounceMs = 150L // Mínimo tiempo entre cambios de dirección
    
    /**
     * Actualiza la posición de la pupila detectada
     * 
     * @param pupilX Coordenada X de la pupila (desde ML Kit)
     * @param pupilY Coordenada Y de la pupila (desde ML Kit)
     */
    fun updatePupilPosition(pupilX: Float, pupilY: Float) {
        if (!calibrationManager.isCalibrated) {
            Log.w(TAG, "Calibration not ready - cannot update position")
            return
        }
        
        // ========================================
        // INVERSIÓN DE EJE X (des-espejado)
        // ========================================
        // La cámara frontal da imagen espejada, necesitamos invertir X
        val mirroredPupilX = cameraImageWidth - pupilX
        
        // Mapear posición de pupila a coordenadas de pantalla usando calibración
        val screenPos = calibrationManager.mapToScreenWeighted(
            mirroredPupilX,  // ← Coordenada X invertida
            pupilY,
            screenWidth, screenHeight
        )
        
        _screenPosition.value = screenPos
        
        // Determinar dirección basada en la posición en pantalla
        updateDirection(screenPos)
        
        // Log para debugging (desactivar en producción)
        // Log.v(TAG, "Pupil ($pupilX, $pupilY) → Mirrored ($mirroredPupilX, $pupilY) → Screen (${screenPos.x}, ${screenPos.y})")
    }
    
    /**
     * Determina la dirección del juego basándose en la posición en pantalla
     * 
     * Divide la pantalla en 9 zonas (grid 3x3):
     * ```
     * UP-LEFT    |   UP      | UP-RIGHT
     * -----------+-----------+-----------
     * LEFT       |  CENTER   | RIGHT
     * -----------+-----------+-----------
     * DOWN-LEFT  |   DOWN    | DOWN-RIGHT
     * ```
     */
    private fun updateDirection(screenPos: PointF) {
        val currentTime = System.currentTimeMillis()
        
        // Debounce: evitar cambios de dirección demasiado rápidos
        if (currentTime - lastDirectionChangeTime < directionDebounceMs) {
            return
        }
        
        // Normalizar posición (0.0 a 1.0)
        val normalizedX = screenPos.x / screenWidth
        val normalizedY = screenPos.y / screenHeight
        
        // Calcular límites de dead zone
        val deadZoneMin = 0.5f - deadZone / 2
        val deadZoneMax = 0.5f + deadZone / 2
        
        val newDirection = when {
            // Centro (dead zone) - sin movimiento
            normalizedX > deadZoneMin && normalizedX < deadZoneMax &&
            normalizedY > deadZoneMin && normalizedY < deadZoneMax -> GameDirection.NONE
            
            // Priorizar eje más pronunciado
            kotlin.math.abs(normalizedX - 0.5f) > kotlin.math.abs(normalizedY - 0.5f) -> {
                // Movimiento horizontal predominante
                if (normalizedX < 0.5f) GameDirection.LEFT else GameDirection.RIGHT
            }
            else -> {
                // Movimiento vertical predominante
                if (normalizedY < 0.5f) GameDirection.UP else GameDirection.DOWN
            }
        }
        
        // Solo actualizar si cambió la dirección
        if (newDirection != _currentDirection.value) {
            _currentDirection.value = newDirection
            lastDirectionChangeTime = currentTime
            Log.d(TAG, "Direction changed to: $newDirection (pos: ${normalizedX.format()}, ${normalizedY.format()})")
        }
    }
    
    /**
     * Configura el tamaño de la zona muerta central
     * 
     * @param deadZone Porcentaje del área central (0.0 a 1.0)
     *                 Por ejemplo, 0.3 = 30% del centro es zona muerta
     */
    fun setDeadZone(deadZone: Float) {
        this.deadZone = deadZone.coerceIn(0f, 0.9f)
        Log.d(TAG, "Dead zone set to ${(this.deadZone * 100).toInt()}%")
    }
    
    /**
     * Obtiene la posición normalizada actual (0.0 a 1.0)
     */
    fun getNormalizedPosition(): Pair<Float, Float> {
        val pos = _screenPosition.value
        return Pair(
            pos.x / screenWidth,
            pos.y / screenHeight
        )
    }
    
    /**
     * Verifica si el sistema está listo para usar
     */
    fun isReady(): Boolean {
        return calibrationManager.isCalibrated
    }
    
    /**
     * Obtiene información de estado para debugging
     */
    fun getStatusInfo(): String {
        val isCalibrated = calibrationManager.isCalibrated
        val pointCount = calibrationManager.getCalibrationCount()
        val pos = _screenPosition.value
        val dir = _currentDirection.value
        
        return buildString {
            appendLine("Pupil Tracking Status:")
            appendLine("  Calibrated: $isCalibrated")
            appendLine("  Points: $pointCount")
            appendLine("  Screen Pos: (${pos.x.format()}, ${pos.y.format()})")
            appendLine("  Direction: $dir")
            appendLine("  Dead Zone: ${(deadZone * 100).toInt()}%")
        }
    }
    
    /**
     * Resetea el controlador
     */
    fun reset() {
        _screenPosition.value = PointF(screenWidth / 2f, screenHeight / 2f)
        _currentDirection.value = GameDirection.NONE
        lastDirectionChangeTime = 0L
    }
    
    companion object {
        private const val TAG = "PupilTracking"
        
        // Extension para formatear floats
        private fun Float.format() = "%.2f".format(this)
    }
}

/**
 * Versión alternativa: Control por zonas (Snake-style)
 * 
 * Divide la pantalla en 5 zonas: 4 direcciones + centro
 * Más simple y directo que el análisis de posición
 */
class ZoneBasedPupilController(
    private val screenWidth: Int,
    private val screenHeight: Int,
    private val calibrationManager: CalibrationManager
) {
    private val _currentZone = MutableStateFlow(Zone.CENTER)
    val currentZone: StateFlow<Zone> = _currentZone.asStateFlow()
    
    // Dimensiones de la imagen de la cámara (para inversión de eje X)
    private val cameraImageWidth = 480f
    private val cameraImageHeight = 640f
    
    enum class Zone {
        CENTER, TOP, BOTTOM, LEFT, RIGHT
    }
    
    /**
     * Actualiza basándose en zonas fijas
     */
    fun updatePupilPosition(pupilX: Float, pupilY: Float) {
        if (!calibrationManager.isCalibrated) return
        
        // INVERSIÓN DE EJE X (des-espejado)
        val mirroredPupilX = cameraImageWidth - pupilX
        
        val screenPos = calibrationManager.mapToScreenWeighted(
            mirroredPupilX,  // ← Coordenada X invertida
            pupilY,
            screenWidth, screenHeight
        )
        
        val normalizedX = screenPos.x / screenWidth
        val normalizedY = screenPos.y / screenHeight
        
        // Dividir en 5 zonas
        val newZone = when {
            // Zonas externas (25% en cada borde)
            normalizedX < 0.25f -> Zone.LEFT
            normalizedX > 0.75f -> Zone.RIGHT
            normalizedY < 0.25f -> Zone.TOP
            normalizedY > 0.75f -> Zone.BOTTOM
            else -> Zone.CENTER
        }
        
        if (newZone != _currentZone.value) {
            _currentZone.value = newZone
        }
    }
    
    /**
     * Convierte zona a GameDirection
     */
    fun getDirection(): GameDirection {
        return when (_currentZone.value) {
            Zone.TOP -> GameDirection.UP
            Zone.BOTTOM -> GameDirection.DOWN
            Zone.LEFT -> GameDirection.LEFT
            Zone.RIGHT -> GameDirection.RIGHT
            Zone.CENTER -> GameDirection.NONE
        }
    }
}
