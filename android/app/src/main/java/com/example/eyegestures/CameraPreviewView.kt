package com.example.eyegestures

import android.content.Context
import android.util.Log
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.face.Face
import com.google.mlkit.vision.face.FaceDetection
import com.google.mlkit.vision.face.FaceDetectorOptions
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

@Composable
fun CameraPreviewView(
    onPupilPositionDetected: (Float, Float) -> Unit = { _, _ -> },
    enableSmoothing: Boolean = true,  // Controlar suavizado
    onFaceDetected: ((Boolean) -> Unit)? = null  // ← Nuevo: callback para detección de rostro
) {
    val lifecycleOwner = LocalLifecycleOwner.current
    
    val cameraExecutor = remember { Executors.newSingleThreadExecutor() }
    val faceAnalyzer = remember(enableSmoothing) {  // Recrear si cambia enableSmoothing
        FaceAnalyzer(
            onPupilPositionDetected = onPupilPositionDetected,
            enableSmoothing = enableSmoothing,
            onFaceDetected = onFaceDetected  // ← Pasar callback
        )
    }
    
    DisposableEffect(Unit) {
        onDispose {
            cameraExecutor.shutdown()
        }
    }
    
    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                val previewView = PreviewView(ctx)
                startCamera(ctx, lifecycleOwner, previewView, faceAnalyzer, cameraExecutor)
                previewView
            },
            modifier = Modifier.fillMaxSize()
        )
    }
}

private fun startCamera(
    context: Context,
    lifecycleOwner: androidx.lifecycle.LifecycleOwner,
    previewView: PreviewView,
    faceAnalyzer: FaceAnalyzer,
    cameraExecutor: ExecutorService
) {
    val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
    
    cameraProviderFuture.addListener({
        val cameraProvider = cameraProviderFuture.get()
        
        // Preview
        val preview = Preview.Builder()
            .build()
            .also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }
        
        // Image Analysis para ML Kit
        val imageAnalysis = ImageAnalysis.Builder()
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()
            .also {
                it.setAnalyzer(cameraExecutor, faceAnalyzer)
            }
        
        // Seleccionar cámara frontal
        val cameraSelector = CameraSelector.DEFAULT_FRONT_CAMERA
        
        try {
            // Desenlazar casos de uso antes de reenlazar
            cameraProvider.unbindAll()
            
            // Enlazar casos de uso a la cámara
            cameraProvider.bindToLifecycle(
                lifecycleOwner,
                cameraSelector,
                preview,
                imageAnalysis
            )
            
        } catch (e: Exception) {
            Log.e("CameraX", "Error al iniciar cámara", e)
        }
        
    }, ContextCompat.getMainExecutor(context))
}
