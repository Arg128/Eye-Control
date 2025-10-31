package com.example.eyegestures

import android.graphics.PointF
import kotlin.math.sqrt

/**
 * Gestiona la calibración del seguimiento de pupila
 * 
 * Mapea la posición de la pupila (coordenadas en la imagen del ojo)
 * a coordenadas de pantalla (pixels en la pantalla del dispositivo).
 * 
 * Proceso de calibración:
 * 1. Mostrar 9 puntos en la pantalla (patrón 3x3)
 * 2. Usuario mira cada punto durante 2 segundos
 * 3. Capturar posición de la pupila para cada punto
 * 4. Crear mapeo pupila → pantalla
 */
class CalibrationManager {
    
    // Puntos de calibración (posición de pupila -> posición en pantalla)
    private val calibrationPoints = mutableListOf<CalibrationPoint>()
    
    // ¿Está calibrado?
    var isCalibrated = false
        private set
    
    // Límites de la pupila durante calibración
    private var minPupilX = Float.MAX_VALUE
    private var maxPupilX = Float.MIN_VALUE
    private var minPupilY = Float.MAX_VALUE
    private var maxPupilY = Float.MIN_VALUE
    
    /**
     * Representa un punto de calibración
     * @param pupilPosition Posición de la pupila en la imagen del ojo
     * @param screenPosition Posición correspondiente en la pantalla
     */
    data class CalibrationPoint(
        val pupilPosition: PointF,  // Posición de la pupila
        val screenPosition: PointF  // Posición en pantalla
    )
    
    /**
     * Agrega un punto de calibración
     * 
     * @param pupilX Posición X de la pupila en la imagen del ojo
     * @param pupilY Posición Y de la pupila en la imagen del ojo
     * @param screenX Coordenada X en la pantalla (pixels)
     * @param screenY Coordenada Y en la pantalla (pixels)
     */
    fun addCalibrationPoint(
        pupilX: Float,
        pupilY: Float,
        screenX: Float,
        screenY: Float
    ) {
        calibrationPoints.add(
            CalibrationPoint(
                PointF(pupilX, pupilY),
                PointF(screenX, screenY)
            )
        )
        
        // Actualizar límites
        minPupilX = minOf(minPupilX, pupilX)
        maxPupilX = maxOf(maxPupilX, pupilX)
        minPupilY = minOf(minPupilY, pupilY)
        maxPupilY = maxOf(maxPupilY, pupilY)
        
        // Se necesitan al menos 4 puntos para calibrar (las 4 esquinas mínimo)
        if (calibrationPoints.size >= 4) {
            isCalibrated = true
        }
    }
    
    /**
     * Convierte posición de pupila a coordenadas de pantalla
     * 
     * Usa interpolación lineal basada en normalización:
     * 1. Normaliza la posición de la pupila (0.0 a 1.0)
     * 2. Mapea al espacio de pantalla
     * 
     * @param pupilX Posición X de la pupila
     * @param pupilY Posición Y de la pupila
     * @param screenWidth Ancho de la pantalla en pixels
     * @param screenHeight Alto de la pantalla en pixels
     * @return PointF con las coordenadas en pantalla
     */
    fun mapToScreen(
        pupilX: Float,
        pupilY: Float,
        screenWidth: Int,
        screenHeight: Int
    ): PointF {
        if (!isCalibrated || calibrationPoints.isEmpty()) {
            // Sin calibración, devolver centro de pantalla
            return PointF(screenWidth / 2f, screenHeight / 2f)
        }
        
        // Normalizar posición de la pupila (0.0 a 1.0)
        val normalizedX = if (maxPupilX != minPupilX) {
            ((pupilX - minPupilX) / (maxPupilX - minPupilX)).coerceIn(0f, 1f)
        } else 0.5f
        
        val normalizedY = if (maxPupilY != minPupilY) {
            ((pupilY - minPupilY) / (maxPupilY - minPupilY)).coerceIn(0f, 1f)
        } else 0.5f
        
        // Mapear a coordenadas de pantalla
        val screenX = normalizedX * screenWidth
        val screenY = normalizedY * screenHeight
        
        return PointF(screenX, screenY)
    }
    
    /**
     * Versión avanzada: usa interpolación ponderada por distancia
     * 
     * Encuentra los 3 puntos de calibración más cercanos y hace un promedio
     * ponderado inversamente proporcional a la distancia.
     * 
     * Más preciso que la normalización lineal, especialmente en los extremos.
     * 
     * @param pupilX Posición X de la pupila
     * @param pupilY Posición Y de la pupila
     * @param screenWidth Ancho de la pantalla
     * @param screenHeight Alto de la pantalla
     * @return PointF con las coordenadas en pantalla
     */
    fun mapToScreenWeighted(
        pupilX: Float,
        pupilY: Float,
        screenWidth: Int,
        screenHeight: Int
    ): PointF {
        if (!isCalibrated || calibrationPoints.isEmpty()) {
            return PointF(screenWidth / 2f, screenHeight / 2f)
        }
        
        // Si solo hay 1 punto, usar ese punto
        if (calibrationPoints.size == 1) {
            return calibrationPoints[0].screenPosition
        }
        
        // Encontrar los 3 puntos de calibración más cercanos
        val sortedPoints = calibrationPoints.sortedBy { point ->
            val dx = point.pupilPosition.x - pupilX
            val dy = point.pupilPosition.y - pupilY
            dx * dx + dy * dy  // Distancia euclidiana al cuadrado (más rápido)
        }
        
        val nearestPoints = sortedPoints.take(minOf(3, calibrationPoints.size))
        
        // Calcular pesos inversamente proporcionales a la distancia
        val weights = nearestPoints.map { point ->
            val dx = point.pupilPosition.x - pupilX
            val dy = point.pupilPosition.y - pupilY
            val distance = sqrt((dx * dx + dy * dy).toDouble())
            // Si la distancia es muy pequeña, dar mucho peso
            if (distance < 0.001) 1000.0 else 1.0 / distance
        }
        
        val totalWeight = weights.sum()
        
        // Promedio ponderado
        var screenX = 0f
        var screenY = 0f
        
        nearestPoints.forEachIndexed { index, point ->
            val weight = (weights[index] / totalWeight).toFloat()
            screenX += point.screenPosition.x * weight
            screenY += point.screenPosition.y * weight
        }
        
        return PointF(
            screenX.coerceIn(0f, screenWidth.toFloat()),
            screenY.coerceIn(0f, screenHeight.toFloat())
        )
    }
    
    /**
     * Reinicia la calibración
     * Borra todos los puntos de calibración almacenados
     */
    fun reset() {
        calibrationPoints.clear()
        isCalibrated = false
        minPupilX = Float.MAX_VALUE
        maxPupilX = Float.MIN_VALUE
        minPupilY = Float.MAX_VALUE
        maxPupilY = Float.MIN_VALUE
    }
    
    /**
     * Devuelve los puntos de calibración necesarios (patrón 3x3)
     * 
     * Patrón de 9 puntos:
     * ```
     * 1---2---3
     * |   |   |
     * 4---5---6
     * |   |   |
     * 7---8---9
     * ```
     * 
     * Los valores son normalizados (0.0 a 1.0), deben multiplicarse
     * por el ancho/alto de la pantalla para obtener pixels.
     * 
     * @return Lista de 9 puntos normalizados (0.0 a 1.0)
     */
    fun getCalibrationPattern(): List<PointF> {
        return listOf(
            // Fila superior
            PointF(0.1f, 0.1f),     // 1. Superior izquierda
            PointF(0.5f, 0.1f),     // 2. Superior centro
            PointF(0.9f, 0.1f),     // 3. Superior derecha
            
            // Fila media
            PointF(0.1f, 0.5f),     // 4. Centro izquierda
            PointF(0.5f, 0.5f),     // 5. Centro
            PointF(0.9f, 0.5f),     // 6. Centro derecha
            
            // Fila inferior
            PointF(0.1f, 0.9f),     // 7. Inferior izquierda
            PointF(0.5f, 0.9f),     // 8. Inferior centro
            PointF(0.9f, 0.9f)      // 9. Inferior derecha
        )
    }
    
    /**
     * Patrón de calibración simple de 5 puntos (más rápido)
     * 
     * ```
     * 1-------2
     * |   3   |
     * 4-------5
     * ```
     */
    fun getSimpleCalibrationPattern(): List<PointF> {
        return listOf(
            PointF(0.1f, 0.1f),     // Superior izquierda
            PointF(0.9f, 0.1f),     // Superior derecha
            PointF(0.5f, 0.5f),     // Centro
            PointF(0.1f, 0.9f),     // Inferior izquierda
            PointF(0.9f, 0.9f)      // Inferior derecha
        )
    }
    
    /**
     * Obtiene el número de puntos de calibración actuales
     */
    fun getCalibrationCount(): Int = calibrationPoints.size
    
    /**
     * Verifica si la calibración es de buena calidad
     * 
     * @return true si hay al menos 5 puntos y cubren suficiente área
     */
    fun isGoodCalibration(): Boolean {
        if (calibrationPoints.size < 5) return false
        
        // Verificar que los puntos cubren un área razonable
        val rangeX = maxPupilX - minPupilX
        val rangeY = maxPupilY - minPupilY
        
        // Los puntos deben cubrir al menos el 30% del espacio
        return rangeX > 0 && rangeY > 0
    }
}
