package com.example.eyegestures

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * Cursor visual que muestra dónde está mirando el usuario
 * 
 * Este componente debe superponerse en todas las pantallas después de la calibración
 * para dar feedback visual de dónde está la mirada del usuario.
 */
@Composable
fun GazeCursor(
    gazePosition: Offset,
    isVisible: Boolean = true,
    modifier: Modifier = Modifier
) {
    if (!isVisible) return
    
    Canvas(modifier = modifier.fillMaxSize()) {
        // Círculo exterior semi-transparente (más grande)
        drawCircle(
            color = Color(0xFF00FF00).copy(alpha = 0.2f),
            radius = 40f,
            center = gazePosition
        )
        
        // Círculo medio
        drawCircle(
            color = Color(0xFF00FF00).copy(alpha = 0.4f),
            radius = 25f,
            center = gazePosition
        )
        
        // Círculo interior con borde
        drawCircle(
            color = Color(0xFF00FF00).copy(alpha = 0.6f),
            radius = 15f,
            center = gazePosition
        )
        
        // Punto central brillante
        drawCircle(
            color = Color(0xFF00FF00),
            radius = 5f,
            center = gazePosition
        )
        
        // Cruz central para precisión
        drawLine(
            color = Color.White.copy(alpha = 0.8f),
            start = Offset(gazePosition.x - 10f, gazePosition.y),
            end = Offset(gazePosition.x + 10f, gazePosition.y),
            strokeWidth = 2f
        )
        
        drawLine(
            color = Color.White.copy(alpha = 0.8f),
            start = Offset(gazePosition.x, gazePosition.y - 10f),
            end = Offset(gazePosition.x, gazePosition.y + 10f),
            strokeWidth = 2f
        )
    }
}

/**
 * ViewModel o Manager global para el cursor de mirada
 * 
 * Usa esto para compartir la posición del cursor entre todas las pantallas
 */
object GazeCursorManager {
    private val _gazePosition = MutableStateFlow(Offset.Zero)
    val gazePosition: StateFlow<Offset> = _gazePosition
    
    private val _isCalibrated = MutableStateFlow(false)
    val isCalibrated: StateFlow<Boolean> = _isCalibrated
    
    /**
     * Actualiza la posición del cursor basado en la posición de la pupila calibrada
     */
    fun updateGazePosition(screenX: Float, screenY: Float) {
        _gazePosition.value = Offset(screenX, screenY)
    }
    
    /**
     * Marca que la calibración se completó
     */
    fun setCalibrated(calibrated: Boolean) {
        _isCalibrated.value = calibrated
    }
    
    /**
     * Verifica si el sistema está calibrado
     */
    fun isCalibrated(): Boolean {
        return _isCalibrated.value
    }
}
