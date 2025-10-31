package com.example.eyegestures

import android.annotation.SuppressLint
import android.graphics.PointF
import android.util.Log
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.face.Face
import com.google.mlkit.vision.face.FaceDetection
import com.google.mlkit.vision.face.FaceDetector
import com.google.mlkit.vision.face.FaceDetectorOptions
import com.google.mlkit.vision.face.FaceContour
import kotlin.math.sqrt

/**
 * FaceAnalyzer - Detección de mirada usando ML Kit Face Detection
 * 
 * ALGORITMO BASADO EN PROYECTO WEB (eyegestures.js):
 * - Usa contornos completos de los ojos (left/right eye contours)
 * - Calcula centro de los ojos como punto base
 * - Aplica factores de escala para compensar distancia a cámara
 * - NO depende de ángulos Euler (movimiento de cabeza)
 * - Usa landmarks REALES de los ojos
 */
class FaceAnalyzer(
    private val onPupilPositionDetected: (Float, Float) -> Unit = { _, _ -> },
    private val enableSmoothing: Boolean = true,
    private val onFaceDetected: ((Boolean) -> Unit)? = null  // Callback para detección de rostro
) : ImageAnalysis.Analyzer {
    
    private val faceDetector: FaceDetector
    
    // Rastreo de escala de cabeza (como scale_x, scale_y en web)
    private var startWidth: Float = 0f
    private var startHeight: Float = 0f
    private var initialEyeDistance: Float? = null
    
    // Posición inicial de cabeza para compensación
    private var headStartingPosX: Float = 0f
    private var headStartingPosY: Float = 0f
    
    // Buffer de suavizado (20 puntos como en web project)
    private val smoothingBuffer = SmoothingBuffer(maxSize = 20)
    
    init {
        // Configurar ML Kit Face Detection
        // IMPORTANTE: Necesitamos CONTOURS para obtener los puntos exactos de los ojos
        val options = FaceDetectorOptions.Builder()
            .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_ACCURATE)  // Más preciso
            .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_NONE)
            .setLandmarkMode(FaceDetectorOptions.LANDMARK_MODE_ALL)  // Todos los landmarks
            .setContourMode(FaceDetectorOptions.CONTOUR_MODE_ALL)    // CRÍTICO: Contornos de ojos
            .setMinFaceSize(0.15f)
            .enableTracking()
            .build()
        
        faceDetector = FaceDetection.getClient(options)
    }
    
    @SuppressLint("UnsafeOptInUsageError")
    override fun analyze(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image
        if (mediaImage != null) {
            val image = InputImage.fromMediaImage(
                mediaImage,
                imageProxy.imageInfo.rotationDegrees
            )
            
            faceDetector.process(image)
                .addOnSuccessListener { faces ->
                    processFaces(faces, imageProxy.width, imageProxy.height)
                }
                .addOnFailureListener { e ->
                    Log.e("FaceAnalyzer", "Error en detección de rostro", e)
                    onFaceDetected?.invoke(false)
                }
                .addOnCompleteListener {
                    imageProxy.close()
                }
        } else {
            imageProxy.close()
        }
    }
    
    private fun processFaces(faces: List<Face>, imageWidth: Int, imageHeight: Int) {
        if (faces.isEmpty()) {
            onFaceDetected?.invoke(false)
            return
        }
        
        onFaceDetected?.invoke(true)
        
        // Procesar la primera cara detectada
        val face = faces[0]
        
        // Detectar posición de mirada usando contornos de ojos
        detectEyeGazePosition(face, imageWidth.toFloat(), imageHeight.toFloat())
    }
    
    /**
     * Detecta la posición de la mirada usando contornos de los ojos
     * 
     * REPLICANDO ALGORITMO DEL PROYECTO WEB:
     * 1. Obtener todos los puntos de contorno de ambos ojos
     * 2. Calcular bounding box de todos los landmarks de la cara
     * 3. Normalizar coordenadas de ojos respecto a bounding box
     * 4. Aplicar factores de escala (compensar distancia a cámara)
     * 5. Calcular centro de los ojos como posición de mirada
     */
    private fun detectEyeGazePosition(face: Face, imageWidth: Float, imageHeight: Float) {
        // Obtener contornos de los ojos (equivalente a LEFT_EYE_KEYPOINTS y RIGHT_EYE_KEYPOINTS en web)
        val leftEyeContour = face.getContour(FaceContour.LEFT_EYE)
        val rightEyeContour = face.getContour(FaceContour.RIGHT_EYE)
        
        // También obtenemos landmarks básicos como fallback
        val leftEyeLandmark = face.getLandmark(com.google.mlkit.vision.face.FaceLandmark.LEFT_EYE)
        val rightEyeLandmark = face.getLandmark(com.google.mlkit.vision.face.FaceLandmark.RIGHT_EYE)
        
        if (leftEyeContour == null || rightEyeContour == null) {
            // Fallback: usar landmarks básicos si contornos no disponibles
            if (leftEyeLandmark != null && rightEyeLandmark != null) {
                processEyeGazeFallback(face, leftEyeLandmark.position, rightEyeLandmark.position, imageWidth, imageHeight)
            }
            return
        }
        
        val leftEyePoints = leftEyeContour.points
        val rightEyePoints = rightEyeContour.points
        
        // ========================================
        // PASO 1: Calcular bounding box de toda la cara
        // (equivalente a offset_x, offset_y, width, height en web)
        // ========================================
        val allFacePoints = mutableListOf<PointF>()
        
        // Agregar todos los contornos disponibles
        face.getContour(FaceContour.FACE)?.points?.let { allFacePoints.addAll(it) }
        allFacePoints.addAll(leftEyePoints)
        allFacePoints.addAll(rightEyePoints)
        
        if (allFacePoints.isEmpty()) {
            return
        }
        
        var minX = Float.MAX_VALUE
        var minY = Float.MAX_VALUE
        var maxX = Float.MIN_VALUE
        var maxY = Float.MIN_VALUE
        
        allFacePoints.forEach { point ->
            minX = minOf(minX, point.x)
            minY = minOf(minY, point.y)
            maxX = maxOf(maxX, point.x)
            maxY = maxOf(maxY, point.y)
        }
        
        val offsetX = minX
        val offsetY = minY
        val width = maxX - minX
        val height = maxY - minY
        
        // ========================================
        // PASO 2: Establecer escala inicial (primera vez)
        // (equivalente a start_width, start_height en web)
        // ========================================
        if (startWidth == 0f || startHeight == 0f) {
            startWidth = width
            startHeight = height
        }
        
        val scaleX = width / startWidth
        val scaleY = height / startHeight
        
        // ========================================
        // PASO 3: Normalizar coordenadas de ojos y aplicar escala
        // (equivalente a left_eye_coordinates y right_eye_coordinates en web)
        // ========================================
        val leftEyeCoordinates = leftEyePoints.map { point ->
            PointF(
                ((point.x - offsetX) / width) * scaleX,
                ((point.y - offsetY) / height) * scaleY
            )
        }
        
        val rightEyeCoordinates = rightEyePoints.map { point ->
            PointF(
                ((point.x - offsetX) / width) * scaleX,
                ((point.y - offsetY) / height) * scaleY
            )
        }
        
        // ========================================
        // PASO 4: Calcular centro de cada ojo
        // ========================================
        val leftEyeCenter = calculateCenter(leftEyeCoordinates)
        val rightEyeCenter = calculateCenter(rightEyeCoordinates)
        
        // Centro entre ambos ojos (posición de mirada base)
        val gazeCenterX = (leftEyeCenter.x + rightEyeCenter.x) / 2f
        val gazeCenterY = (leftEyeCenter.y + rightEyeCenter.y) / 2f
        
        // ========================================
        // PASO 5: Compensar movimiento de cabeza
        // (equivalente a head_starting_pos en web)
        // ========================================
        if (headStartingPosX == 0f && headStartingPosY == 0f) {
            headStartingPosX = offsetX * scaleX
            headStartingPosY = offsetY * scaleY
        }
        
        val headOffsetX = (offsetX * scaleX) - headStartingPosX
        val headOffsetY = (offsetY * scaleY) - headStartingPosY
        
        // ========================================
        // PASO 6: Calcular posición final de mirada en coordenadas de imagen
        // ========================================
        // Convertir coordenadas normalizadas de vuelta a pixels de imagen
        val pupilX = offsetX + (gazeCenterX * width) + (headOffsetX * 0.5f)
        val pupilY = offsetY + (gazeCenterY * height) + (headOffsetY * 0.5f)
        
        // ========================================
        // PASO 7: Suavizado condicional
        // ========================================
        if (enableSmoothing) {
            smoothingBuffer.push(pupilX, pupilY)
            val smoothed = smoothingBuffer.getSmoothed()
            
            if (smoothed != null) {
                onPupilPositionDetected(smoothed.x, smoothed.y)
                Log.d("FaceAnalyzer", "Gaze SMOOTHED: (${smoothed.x}, ${smoothed.y}), Scale: ($scaleX, $scaleY)")
            } else {
                onPupilPositionDetected(pupilX, pupilY)
            }
        } else {
            onPupilPositionDetected(pupilX, pupilY)
            Log.d("FaceAnalyzer", "Gaze RAW: ($pupilX, $pupilY), Scale: ($scaleX, $scaleY)")
        }
    }
    
    /**
     * Fallback cuando los contornos no están disponibles
     * Usa landmarks básicos de ojos + ángulos Euler como aproximación
     */
    @Suppress("UNUSED_PARAMETER")
    private fun processEyeGazeFallback(
        face: Face,
        leftEyePos: PointF,
        rightEyePos: PointF,
        imageWidth: Float,
        imageHeight: Float
    ) {
        // Calcular distancia entre ojos para factor de escala
        val eyeDistance = sqrt(
            (rightEyePos.x - leftEyePos.x) * (rightEyePos.x - leftEyePos.x) +
            (rightEyePos.y - leftEyePos.y) * (rightEyePos.y - leftEyePos.y)
        )
        
        if (initialEyeDistance == null) {
            initialEyeDistance = eyeDistance
        }
        
        val scale = eyeDistance / (initialEyeDistance ?: eyeDistance)
        
        // Centro entre ojos
        val baseX = (leftEyePos.x + rightEyePos.x) / 2f
        val baseY = (leftEyePos.y + rightEyePos.y) / 2f
        
        // Usar Euler angles como aproximación (menos preciso)
        val eulerY = face.headEulerAngleY
        val eulerX = face.headEulerAngleX
        
        val offsetX = eulerY * 8f * scale
        val offsetY = eulerX * 6f * scale
        
        val pupilX = baseX + offsetX
        val pupilY = baseY + offsetY
        
        if (enableSmoothing) {
            smoothingBuffer.push(pupilX, pupilY)
            val smoothed = smoothingBuffer.getSmoothed()
            if (smoothed != null) {
                onPupilPositionDetected(smoothed.x, smoothed.y)
            } else {
                onPupilPositionDetected(pupilX, pupilY)
            }
        } else {
            onPupilPositionDetected(pupilX, pupilY)
        }
        
        Log.w("FaceAnalyzer", "Using fallback mode (Euler angles) - less accurate")
    }
    
    /**
     * Calcula el centro geométrico de un conjunto de puntos
     */
    private fun calculateCenter(points: List<PointF>): PointF {
        if (points.isEmpty()) {
            return PointF(0f, 0f)
        }
        
        var sumX = 0f
        var sumY = 0f
        
        points.forEach { point ->
            sumX += point.x
            sumY += point.y
        }
        
        return PointF(sumX / points.size, sumY / points.size)
    }
}
