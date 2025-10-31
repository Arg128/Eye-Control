package com.example.eyegestures

import android.graphics.Bitmap
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * Ventana de diagnóstico para mostrar el procesamiento de OpenCV durante calibración
 * 
 * Muestra:
 * - Vista en blanco y negro del ojo procesado
 * - Punto rojo sobre la pupila detectada
 * - Coordenadas en tiempo real
 */
@Composable
fun DiagnosticWindow(
    processedFrame: Bitmap?,
    pupilPosition: Offset?,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .size(200.dp, 150.dp)
            .background(Color.Black, RoundedCornerShape(8.dp))
            .border(2.dp, Color(0xFF00FF00), RoundedCornerShape(8.dp))
            .padding(8.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Título
            Text(
                text = "🔍 Diagnóstico",
                color = Color(0xFF00FF00),
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(4.dp))
            
            // Vista del frame procesado
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .background(Color.DarkGray, RoundedCornerShape(4.dp))
            ) {
                if (processedFrame != null) {
                    // Imagen procesada de OpenCV
                    Image(
                        bitmap = processedFrame.asImageBitmap(),
                        contentDescription = "Processed Eye",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Fit
                    )
                    
                    // Punto rojo sobre la pupila detectada
                    if (pupilPosition != null) {
                        Canvas(modifier = Modifier.fillMaxSize()) {
                            // Escalar la posición de la pupila al tamaño del canvas
                            val scaleX = size.width / processedFrame.width
                            val scaleY = size.height / processedFrame.height
                            
                            val scaledX = pupilPosition.x * scaleX
                            val scaledY = pupilPosition.y * scaleY
                            
                            // Círculo rojo exterior
                            drawCircle(
                                color = Color.Red,
                                radius = 12f,
                                center = Offset(scaledX, scaledY)
                            )
                            
                            // Círculo blanco interior
                            drawCircle(
                                color = Color.White,
                                radius = 6f,
                                center = Offset(scaledX, scaledY)
                            )
                            
                            // Punto central
                            drawCircle(
                                color = Color.Red,
                                radius = 2f,
                                center = Offset(scaledX, scaledY)
                            )
                        }
                    }
                } else {
                    // Placeholder cuando no hay frame
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "Esperando\nOpenCV...",
                            color = Color.White.copy(alpha = 0.5f),
                            fontSize = 10.sp,
                            textAlign = androidx.compose.ui.text.style.TextAlign.Center
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(4.dp))
            
            // Coordenadas
            Text(
                text = if (pupilPosition != null) {
                    "X: %.1f, Y: %.1f".format(pupilPosition.x, pupilPosition.y)
                } else {
                    "Pupila: --"
                },
                color = Color(0xFF00FF00),
                fontSize = 10.sp,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

/**
 * Manager global para compartir datos de diagnóstico
 */
object DiagnosticManager {
    private val _processedFrame = MutableStateFlow<Bitmap?>(null)
    val processedFrame: StateFlow<Bitmap?> = _processedFrame
    
    private val _pupilPosition = MutableStateFlow<Offset?>(null)
    val pupilPosition: StateFlow<Offset?> = _pupilPosition
    
    private val _isEnabled = MutableStateFlow(true)
    val isEnabled: StateFlow<Boolean> = _isEnabled
    
    /**
     * Actualiza el frame procesado de OpenCV
     */
    fun updateProcessedFrame(bitmap: Bitmap?) {
        _processedFrame.value = bitmap
    }
    
    /**
     * Actualiza la posición de la pupila detectada
     */
    fun updatePupilPosition(x: Float, y: Float) {
        _pupilPosition.value = Offset(x, y)
    }
    
    /**
     * Limpia la posición de la pupila
     */
    fun clearPupilPosition() {
        _pupilPosition.value = null
    }
    
    /**
     * Habilita/deshabilita el diagnóstico
     */
    fun setEnabled(enabled: Boolean) {
        _isEnabled.value = enabled
    }
}
