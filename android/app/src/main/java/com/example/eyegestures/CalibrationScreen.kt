package com.example.eyegestures

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.google.mlkit.vision.face.Face
import kotlinx.coroutines.delay

/**
 * Pantalla de Calibración con ViewModel integrado
 * 
 * Proceso:
 * 1. Usuario inicia calibración
 * 2. ViewModel mueve círculo a posición 1
 * 3. Usuario mira fijamente 2 segundos
 * 4. onPointCaptured() captura pupila + objetivo
 * 5. ViewModel avanza al siguiente punto
 * 6. Repite hasta 25 puntos
 * 7. Navega automáticamente al menú
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CalibrationScreen(
    onCalibrationComplete: (List<CalibrationPoint>) -> Unit,
    onBack: () -> Unit,
    viewModel: CalibrationViewModel = viewModel()
) {
    val configuration = LocalConfiguration.current
    val density = LocalDensity.current
    
    // Dimensiones de la pantalla en pixels
    val screenWidthPx = with(density) { configuration.screenWidthDp.dp.toPx().toInt() }
    val screenHeightPx = with(density) { configuration.screenHeightDp.dp.toPx().toInt() }
    
    // Observar estado del ViewModel
    val calibrationState by viewModel.calibrationState.collectAsState()
    val targetPosition by viewModel.targetPosition.collectAsState()
    val currentPointIndex by viewModel.currentPointIndex.collectAsState()
    
    var calibrationStarted by remember { mutableStateOf(false) }
    
    // Animación del círculo (pulso)
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.4f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse"
    )
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Calibración de Mirada") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { paddingValues ->
        
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(Color.Black)
        ) {
            when {
                !calibrationStarted -> {
                    // Pantalla de instrucciones
                    InstructionsView(
                        onStartCalibration = {
                            viewModel.startCalibration(screenWidthPx, screenHeightPx)
                            calibrationStarted = true
                        },
                        onBack = onBack
                    )
                }
                calibrationState is CalibrationState.Calibrating -> {
                    // Countdown con validación de datos
                    var countdown by remember(currentPointIndex) { mutableStateOf(2f) }
                    var attemptingCapture by remember(currentPointIndex) { mutableStateOf(false) }
                    
                    LaunchedEffect(currentPointIndex) {
                        countdown = 2f
                        attemptingCapture = false
                        
                        while (countdown > 0) {
                            delay(50)  // Actualizar cada 50ms
                            countdown -= 0.05f
                        }
                        
                        // Intentar capturar
                        attemptingCapture = true
                        viewModel.onPointCaptured()
                    }
                    
                    // Mostrar punto de calibración actual con feedback
                    CalibrationTargetView(
                        targetPosition = targetPosition,
                        pointNumber = currentPointIndex + 1,
                        totalPoints = (calibrationState as CalibrationState.Calibrating).totalPoints,
                        pulseScale = pulseScale,
                        countdown = countdown,
                        hasValidData = (calibrationState as CalibrationState.Calibrating).hasValidData,
                        onPupilPositionDetected = { pupilX, pupilY ->
                            viewModel.updatePupilPosition(pupilX, pupilY)
                        }
                    )
                }
                calibrationState is CalibrationState.DetectionError -> {
                    // Mostrar error y botón de reintento
                    CalibrationErrorView(
                        errorMessage = (calibrationState as CalibrationState.DetectionError).message,
                        pointNumber = (calibrationState as CalibrationState.DetectionError).currentPoint,
                        onRetry = {
                            viewModel.retryCurrentPoint()
                        },
                        onCancel = {
                            viewModel.cancelCalibration()
                            onBack()
                        }
                    )
                }
                calibrationState is CalibrationState.Completed -> {
                    // Pantalla de calibración completada
                    CalibrationCompletedView(
                        onContinue = {
                            val points = (calibrationState as CalibrationState.Completed).calibratedPoints
                            onCalibrationComplete(points)
                        }
                    )
                }
            }
        }
    }
}

/**
 * Vista de instrucciones inicial
 */
@Composable
private fun InstructionsView(
    onStartCalibration: () -> Unit,
    onBack: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.Visibility,
            contentDescription = null,
            tint = Color.White,
            modifier = Modifier.size(80.dp)
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        Text(
            "Calibración de Seguimiento Ocular",
            color = Color.White,
            fontSize = 26.sp,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = Color.White.copy(alpha = 0.15f)
            )
        ) {
            Column(
                modifier = Modifier.padding(20.dp)
            ) {
                Text(
                    "📌 Instrucciones:",
                    color = Color.White,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                InstructionItem("1️⃣ Mira directamente cada círculo rojo")
                InstructionItem("2️⃣ Mantén la mirada fija hasta que avance")
                InstructionItem("3️⃣ El punto se capturará automáticamente")
                InstructionItem("4️⃣ Repite para los 13 puntos")
                
                Spacer(modifier = Modifier.height(12.dp))
                
                Text(
                    "⏱️ Duración: ~26 segundos",
                    color = Color(0xFF4CAF50),
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
        
        Spacer(modifier = Modifier.height(40.dp))
        
        Button(
            onClick = onStartCalibration,
            modifier = Modifier
                .fillMaxWidth()
                .height(60.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFF4CAF50)
            )
        ) {
            Text(
                "Iniciar Calibración",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        OutlinedButton(
            onClick = onBack,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            colors = ButtonDefaults.outlinedButtonColors(
                contentColor = Color.White
            )
        ) {
            Text("Cancelar", fontSize = 18.sp)
        }
    }
}

@Composable
private fun InstructionItem(text: String) {
    Text(
        text = text,
        color = Color.White,
        fontSize = 17.sp,
        modifier = Modifier.padding(vertical = 4.dp)
    )
}

/**
 * Vista del objetivo de calibración con cámara integrada
 */
@Composable
private fun CalibrationTargetView(
    targetPosition: Offset,
    pointNumber: Int,
    totalPoints: Int,
    pulseScale: Float,
    countdown: Float,
    hasValidData: Boolean,
    onPupilPositionDetected: (Float, Float) -> Unit
) {
    Box(modifier = Modifier.fillMaxSize()) {
        
        // ✅ CÁMARA PARA DETECCIÓN DE PUPILA
        // Sin suavizado durante calibración (posición exacta)
        CameraPreviewView(
            enableSmoothing = false,  // ← CRÍTICO: Sin suavizado en calibración
            onPupilPositionDetected = onPupilPositionDetected
        )
        
        // Círculo objetivo animado (superpuesto sobre la cámara)
        Canvas(modifier = Modifier.fillMaxSize()) {
            // Círculo exterior pulsante (rojo brillante)
            drawCircle(
                color = Color(0xFFFF3D00),
                radius = 50f * pulseScale,
                center = targetPosition
            )
            
            // Círculo medio (rojo oscuro)
            drawCircle(
                color = Color(0xFFD32F2F),
                radius = 35f,
                center = targetPosition
            )
            
            // Círculo interior (blanco)
            drawCircle(
                color = Color.White,
                radius = 15f,
                center = targetPosition
            )
            
            // Punto central (negro)
            drawCircle(
                color = Color.Black,
                radius = 5f,
                center = targetPosition
            )
        }
        
        // Información superior (con fondo semi-transparente para visibilidad)
        Column(
            modifier = Modifier
                .align(Alignment.TopCenter)
                .padding(top = 48.dp)
                .background(Color.Black.copy(alpha = 0.6f))
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                "Punto $pointNumber de $totalPoints",
                color = Color.White,
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = Color.White.copy(alpha = 0.2f)
                )
            ) {
                Text(
                    "👁️ Mira el círculo fijamente",
                    color = Color.White,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(horizontal = 24.dp, vertical = 12.dp)
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Barra de progreso
            LinearProgressIndicator(
                progress = { pointNumber.toFloat() / totalPoints.toFloat() },
                modifier = Modifier
                    .width(250.dp)
                    .height(10.dp),
                color = Color(0xFF4CAF50),
                trackColor = Color.White.copy(alpha = 0.3f),
            )
        }
        
        // Indicador de mirada en la parte inferior
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 60.dp)
                .background(Color.Black.copy(alpha = 0.7f))
                .padding(horizontal = 24.dp, vertical = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Estado de detección
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    imageVector = if (hasValidData) Icons.Default.Visibility else Icons.Default.Warning,
                    contentDescription = null,
                    tint = if (hasValidData) Color(0xFF4CAF50) else Color(0xFFFF9800),
                    modifier = Modifier.size(32.dp)
                )
                
                Text(
                    text = if (hasValidData) {
                        "✓ Rostro detectado"
                    } else {
                        "⚠ Buscando rostro..."
                    },
                    color = if (hasValidData) Color(0xFF4CAF50) else Color(0xFFFF9800),
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Countdown
            Text(
                text = "Capturando en: ${countdown.toInt() + 1}s",
                color = Color.White,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Barra de progreso del countdown
            LinearProgressIndicator(
                progress = { (2f - countdown) / 2f },
                modifier = Modifier
                    .width(200.dp)
                    .height(8.dp),
                color = if (hasValidData) Color(0xFF4CAF50) else Color(0xFFFF9800),
                trackColor = Color.White.copy(alpha = 0.3f),
            )
        }
    }
}

/**
 * Vista de error con opción de reintento
 */
@Composable
private fun CalibrationErrorView(
    errorMessage: String,
    pointNumber: Int,
    onRetry: () -> Unit,
    onCancel: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black.copy(alpha = 0.9f)),
        contentAlignment = Alignment.Center
    ) {
        Card(
            modifier = Modifier.padding(32.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFF1a1a2e)
            )
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    imageVector = Icons.Default.Warning,
                    contentDescription = null,
                    tint = Color(0xFFFF9800),
                    modifier = Modifier.size(64.dp)
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    "Error en Punto $pointNumber",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    errorMessage,
                    fontSize = 16.sp,
                    color = Color.White.copy(alpha = 0.8f),
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
                
                Spacer(modifier = Modifier.height(24.dp))
                
                Button(
                    onClick = onRetry,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF4CAF50)
                    )
                ) {
                    Text(
                        "Reintentar Punto $pointNumber",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                Spacer(modifier = Modifier.height(12.dp))
                
                OutlinedButton(
                    onClick = onCancel,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = Color.White
                    )
                ) {
                    Text("Cancelar Calibración", fontSize = 16.sp)
                }
            }
        }
    }
}

/**
 * Vista de calibración completada exitosamente
 */
@Composable
private fun CalibrationCompletedView(
    onContinue: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Icono de éxito (animado)
        Icon(
            imageVector = Icons.Default.Visibility,
            contentDescription = null,
            tint = Color(0xFF4CAF50),
            modifier = Modifier.size(100.dp)
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Text(
            "✓ Calibración Completa",
            color = Color(0xFF4CAF50),
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            "¡Perfecto!",
            color = Color.White,
            fontSize = 24.sp,
            fontWeight = FontWeight.Medium
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = Color.White.copy(alpha = 0.15f)
            )
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    "Tu sistema de seguimiento ocular está listo.",
                    color = Color.White,
                    fontSize = 18.sp,
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
                
                Spacer(modifier = Modifier.height(12.dp))
                
                Text(
                    "Ahora podrás controlar los juegos con tu mirada.",
                    color = Color.White.copy(alpha = 0.8f),
                    fontSize = 16.sp,
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
            }
        }
        
        Spacer(modifier = Modifier.height(48.dp))
        
        Button(
            onClick = onContinue,
            modifier = Modifier
                .fillMaxWidth()
                .height(60.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFF4CAF50)
            )
        ) {
            Text(
                "Continuar",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}
