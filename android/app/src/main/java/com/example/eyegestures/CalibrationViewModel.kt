package com.example.eyegestures

import android.util.Log
import androidx.compose.ui.geometry.Offset
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel para gestionar el proceso de calibración
 * 
 * Controla:
 * - Posición del círculo objetivo
 * - Captura de datos al parpadear
 * - Progreso de calibración (5 puntos)
 * - Navegación automática al completar
 */
class CalibrationViewModel : ViewModel() {
    
    // Estado de la calibración
    private val _calibrationState = MutableStateFlow<CalibrationState>(CalibrationState.NotStarted)
    val calibrationState: StateFlow<CalibrationState> = _calibrationState.asStateFlow()
    
    // Posición actual del círculo objetivo
    private val _targetPosition = MutableStateFlow(Offset.Zero)
    val targetPosition: StateFlow<Offset> = _targetPosition.asStateFlow()
    
    // Índice del punto actual (0-4)
    private val _currentPointIndex = MutableStateFlow(0)
    val currentPointIndex: StateFlow<Int> = _currentPointIndex.asStateFlow()
    
    // Última posición de la pupila detectada
    private var lastPupilPosition: Pair<Float, Float>? = null
    
    // Auto-avance inteligente: contador de frames cerca del target
    private var framesNearTarget = 0
    private val framesRequiredForCapture = 60  // ~60 frames @ 30fps = 2 segundos
    private val proximityThreshold = 0.1f  // 10% del ancho de pantalla (como en web)
    
    // Dimensiones de la imagen de la cámara (para inversión de eje X)
    // La cámara frontal suele dar 480x640 en portrait
    private val cameraImageWidth = 480f
    private val cameraImageHeight = 640f
    
    // Lista de puntos calibrados
    private val calibratedPoints = mutableListOf<CalibrationPoint>()
    
    // Instancia del gestor de calibración (compartida globalmente)
    private val calibration = CalibrationManager()
    
    // 13 puntos óptimos: esquinas + bordes + cruz central
    // Balance perfecto entre cobertura y velocidad (~26 segundos)
    private val targetPositionsNormalized = listOf(
        // 4 esquinas (críticas para rango completo)
        Offset(0.1f, 0.1f),   // 1. Superior izquierda
        Offset(0.9f, 0.1f),   // 2. Superior derecha
        Offset(0.1f, 0.9f),   // 3. Inferior izquierda
        Offset(0.9f, 0.9f),   // 4. Inferior derecha
        
        // 4 puntos medios de bordes (interpolación de bordes)
        Offset(0.5f, 0.1f),   // 5. Superior centro
        Offset(0.5f, 0.9f),   // 6. Inferior centro
        Offset(0.1f, 0.5f),   // 7. Medio izquierda
        Offset(0.9f, 0.5f),   // 8. Medio derecha
        
        // 4 puntos de cruz central (precisión en área de uso)
        Offset(0.3f, 0.5f),   // 9. Cruz izquierda
        Offset(0.7f, 0.5f),   // 10. Cruz derecha
        Offset(0.5f, 0.3f),   // 11. Cruz superior
        Offset(0.5f, 0.7f),   // 12. Cruz inferior
        
        // 1 punto central (referencia principal)
        Offset(0.5f, 0.5f)    // 13. Centro absoluto
    )
    
    /**
     * Reintentar captura del punto actual después de un error
     */
    fun retryCurrentPoint() {
        val state = _calibrationState.value
        
        if (state is CalibrationState.DetectionError) {
            val calibratingState = CalibrationState.Calibrating(
                currentPoint = state.currentPoint,
                totalPoints = targetPositionsNormalized.size,
                targetPositions = targetPositionsNormalized.map { normalized ->
                    Offset(
                        normalized.x * screenWidth,
                        normalized.y * screenHeight
                    )
                },
                hasValidData = lastPupilPosition != null
            )
            _calibrationState.value = calibratingState
            Log.d(TAG, "Retrying point ${state.currentPoint}")
        }
    }
    
    // Guardar dimensiones de pantalla para retry
    private var screenWidth: Int = 0
    private var screenHeight: Int = 0
    
    /**
     * Inicia el proceso de calibración
     * 
     * @param screenWidth Ancho de la pantalla en pixels
     * @param screenHeight Alto de la pantalla en pixels
     */
    fun startCalibration(screenWidth: Int, screenHeight: Int) {
        Log.d(TAG, "Starting calibration - Screen: ${screenWidth}x${screenHeight}")
        
        // Guardar dimensiones
        this.screenWidth = screenWidth
        this.screenHeight = screenHeight
        
        // Convertir posiciones normalizadas a pixels
        val targetPositions = targetPositionsNormalized.map { normalized ->
            Offset(
                normalized.x * screenWidth,
                normalized.y * screenHeight
            )
        }
        
        // Resetear estado
        _currentPointIndex.value = 0
        calibratedPoints.clear()
        lastPupilPosition = null
        framesNearTarget = 0  // Reset auto-advance counter
        
        // Establecer primera posición
        _targetPosition.value = targetPositions[0]
        _calibrationState.value = CalibrationState.Calibrating(
            currentPoint = 1,
            totalPoints = 13,  // 13 puntos óptimos
            targetPositions = targetPositions
        )
        
        Log.d(TAG, "Target 1/13 at: ${targetPositions[0]}")
    }
    
    /**
     * Actualiza la posición de la pupila detectada por OpenCV
     * 
     * Llama esta función continuamente desde tu detector de OpenCV
     * 
     * @param pupilX Coordenada X de la pupila
     * @param pupilY Coordenada Y de la pupila
     */
    fun updatePupilPosition(pupilX: Float, pupilY: Float) {
        lastPupilPosition = Pair(pupilX, pupilY)
        
        // Actualizar estado para indicar que hay datos válidos
        val state = _calibrationState.value
        if (state is CalibrationState.Calibrating && !state.hasValidData) {
            _calibrationState.value = state.copy(hasValidData = true)
        }
        
        // Auto-avance inteligente: verificar si está mirando el target
        if (state is CalibrationState.Calibrating) {
            checkProximityToTarget(pupilX, pupilY, state)
        }
    }
    
    /**
     * Verifica si actualmente hay datos válidos de pupila
     */
    fun hasPupilData(): Boolean {
        return lastPupilPosition != null
    }
    
    /**
     * Verifica si la pupila está cerca del punto target (auto-avance inteligente)
     * 
     * NOTA: Durante calibración inicial NO podemos mapear pupila → pantalla
     * porque aún no tenemos suficientes puntos calibrados.
     * 
     * Solución: Usar timer fijo (más confiable durante calibración)
     */
    @Suppress("UNUSED_PARAMETER")
    private fun checkProximityToTarget(pupilX: Float, pupilY: Float, state: CalibrationState.Calibrating) {
        // Durante calibración, no podemos usar mapeo pupila→pantalla
        // porque justamente estamos recopilando esos datos.
        // El auto-avance se manejará con timer en CalibrationScreen.kt
        
        // Esta función se mantiene para futuras mejoras con pre-calibración aproximada
    }
    
    /**
     * Función llamada cuando se captura automáticamente un punto (después de 2 segundos)
     * O puede ser llamada manualmente si se desea
     * 
     * Esta es la función CLAVE que conecta todo:
     * 1. Captura la posición actual de la pupila
     * 2. Obtiene la posición del círculo objetivo
     * 3. Envía ambas a calibration.addCalibrationPoint()
     * 4. Avanza al siguiente punto
     * 5. Si termina, indica navegación al menú
     */
    fun onPointCaptured() {
        val state = _calibrationState.value
        
        // Verificar que estamos calibrando
        if (state !is CalibrationState.Calibrating) {
            Log.w(TAG, "Point captured but not calibrating")
            return
        }
        
        // ========================================
        // VALIDACIÓN ROBUSTA: Verificar datos válidos
        // ========================================
        val pupilPos = lastPupilPosition
        if (pupilPos == null) {
            Log.e(TAG, "❌ NO PUPIL DATA - Showing error to user")
            val currentIndex = _currentPointIndex.value
            _calibrationState.value = CalibrationState.DetectionError(
                currentPoint = currentIndex + 1,
                message = "No se detectó tu rostro.\nMira directamente a la cámara."
            )
            return  // NO AVANZAR
        }
        
        // Validar que la posición es razonable (dentro de rango de cámara)
        if (pupilPos.first < 0 || pupilPos.first > cameraImageWidth ||
            pupilPos.second < 0 || pupilPos.second > cameraImageHeight) {
            Log.e(TAG, "❌ INVALID PUPIL POSITION: (${pupilPos.first}, ${pupilPos.second})")
            val currentIndex = _currentPointIndex.value
            _calibrationState.value = CalibrationState.DetectionError(
                currentPoint = currentIndex + 1,
                message = "Posición inválida.\nMantén tu cara centrada en la cámara."
            )
            return  // NO AVANZAR
        }
        
        val currentIndex = _currentPointIndex.value
        val currentTarget = state.targetPositions[currentIndex]
        
        Log.d(TAG, "✅ Point ${currentIndex + 1} captured successfully")
        Log.d(TAG, "  Pupil RAW: (${pupilPos.first}, ${pupilPos.second})")
        Log.d(TAG, "  Target: (${currentTarget.x}, ${currentTarget.y})")
        
        // ========================================
        // INVERSIÓN DE EJE X (des-espejado)
        // ========================================
        // La cámara frontal da imagen espejada, necesitamos invertir X
        val mirroredPupilX = cameraImageWidth - pupilPos.first
        val pupilY = pupilPos.second
        
        Log.d(TAG, "  Pupil MIRRORED: ($mirroredPupilX, $pupilY)")
        
        // ========================================
        // PASO CLAVE: Guardar punto de calibración con coordenadas corregidas
        // ========================================
        calibration.addCalibrationPoint(
            pupilX = mirroredPupilX,  // ← Coordenada X invertida
            pupilY = pupilY,
            screenX = currentTarget.x,
            screenY = currentTarget.y
        )
        
        // Guardar también en lista local para referencia
        calibratedPoints.add(
            CalibrationPoint(
                pupilX = mirroredPupilX,  // ← Coordenada X invertida
                pupilY = pupilY,
                screenX = currentTarget.x,
                screenY = currentTarget.y
            )
        )
        
        // ========================================
        // Avanzar al siguiente punto
        // ========================================
        val nextIndex = currentIndex + 1
        
        if (nextIndex < state.totalPoints) {
            // Aún quedan puntos por calibrar
            _currentPointIndex.value = nextIndex
            _targetPosition.value = state.targetPositions[nextIndex]
            framesNearTarget = 0  // Reset counter para nuevo punto
            
            _calibrationState.value = CalibrationState.Calibrating(
                currentPoint = nextIndex + 1,
                totalPoints = state.totalPoints,
                targetPositions = state.targetPositions
            )
            
            Log.d(TAG, "Moving to target ${nextIndex + 1} at: ${state.targetPositions[nextIndex]}")
        } else {
            // ========================================
            // CALIBRACIÓN COMPLETADA
            // ========================================
            Log.d(TAG, "Calibration completed! ${calibratedPoints.size} points captured")
            
            // Guardar la instancia compartida para que los juegos la usen
            setSharedCalibrationManager(calibration)
            
            // Marcar que el sistema está calibrado (para mostrar cursor)
            GazeCursorManager.setCalibrated(true)
            
            _calibrationState.value = CalibrationState.Completed(
                calibratedPoints = calibratedPoints.toList()
            )
        }
    }
    
    /**
     * Cancela la calibración
     */
    fun cancelCalibration() {
        Log.d(TAG, "Calibration cancelled")
        _calibrationState.value = CalibrationState.Cancelled
        _currentPointIndex.value = 0
        calibratedPoints.clear()
        lastPupilPosition = null
    }
    
    /**
     * Resetea el estado para poder recalibrar
     */
    fun reset() {
        _calibrationState.value = CalibrationState.NotStarted
        _currentPointIndex.value = 0
        calibratedPoints.clear()
        lastPupilPosition = null
    }
    
    /**
     * Obtiene los puntos calibrados
     */
    fun getCalibrationPoints(): List<CalibrationPoint> {
        return calibratedPoints.toList()
    }
    
    /**
     * Verifica si la calibración está activa
     */
    fun isCalibrating(): Boolean {
        return _calibrationState.value is CalibrationState.Calibrating
    }
    
    /**
     * Obtiene la instancia de CalibrationManager configurada
     * Úsala en tus juegos para mapear pupila → pantalla
     */
    fun getCalibrationManager(): CalibrationManager {
        return calibration
    }
    
    companion object {
        private const val TAG = "CalibrationVM"
        
        // Instancia compartida del CalibrationManager para usar en toda la app
        private var sharedCalibrationManager: CalibrationManager? = null
        
        /**
         * Obtiene la instancia global de CalibrationManager
         * Usa esto en tus ViewModels de juegos para acceder a la calibración
         */
        fun getSharedCalibrationManager(): CalibrationManager {
            if (sharedCalibrationManager == null) {
                sharedCalibrationManager = CalibrationManager()
            }
            return sharedCalibrationManager!!
        }
        
        /**
         * Establece la instancia compartida (llamado después de calibrar)
         */
        fun setSharedCalibrationManager(manager: CalibrationManager) {
            sharedCalibrationManager = manager
        }
    }
}

/**
 * Estados posibles de la calibración
 */
sealed class CalibrationState {
    /**
     * Calibración no iniciada
     */
    object NotStarted : CalibrationState()
    
    /**
     * Calibración en progreso
     * 
     * @param currentPoint Punto actual (1-25)
     * @param totalPoints Total de puntos (25)
     * @param targetPositions Lista de posiciones en pixels
     * @param hasValidData Si hay datos válidos de pupila
     */
    data class Calibrating(
        val currentPoint: Int,
        val totalPoints: Int,
        val targetPositions: List<Offset>,
        val hasValidData: Boolean = false
    ) : CalibrationState()
    
    /**
     * Error durante calibración (rostro no detectado)
     * 
     * @param currentPoint Punto actual donde falló
     * @param message Mensaje de error para mostrar al usuario
     */
    data class DetectionError(
        val currentPoint: Int,
        val message: String
    ) : CalibrationState()
    
    /**
     * Calibración completada exitosamente
     * 
     * @param calibratedPoints Lista de puntos calibrados
     */
    data class Completed(
        val calibratedPoints: List<CalibrationPoint>
    ) : CalibrationState()
    
    /**
     * Calibración cancelada por el usuario
     */
    object Cancelled : CalibrationState()
}

/**
 * Data class para un punto de calibración
 */
data class CalibrationPoint(
    val pupilX: Float,      // Posición X de la pupila (OpenCV)
    val pupilY: Float,      // Posición Y de la pupila (OpenCV)
    val screenX: Float,     // Coordenada X del objetivo en pantalla
    val screenY: Float      // Coordenada Y del objetivo en pantalla
)
