package com.example.eyegestures

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlin.math.sin

/**
 * Pantalla completa del juego Snake con ViewModel
 * Incluye:
 * - Canvas para dibujar la serpiente y la comida
 * - Controles de dirección (táctiles y por mirada)
 * - Integración con Eye Gestures
 * - Sistema de puntuación
 * - Observable state desde ViewModel
 */
@Composable
fun SnakeScreen(
    onBack: () -> Unit = {},
    viewModel: SnakeViewModel = androidx.lifecycle.viewmodel.compose.viewModel()
) {
    // Observar estado del juego desde ViewModel
    val gameState by viewModel.gameState.collectAsState()
    
    var showEyeGestures by remember { mutableStateOf(true) }
    
    // Observar el cursor de mirada
    val isCalibrated by GazeCursorManager.isCalibrated.collectAsState()
    val gazePosition by GazeCursorManager.gazePosition.collectAsState()
    
    // ✅ CÁMARA INVISIBLE SIEMPRE ACTIVA (para seguimiento ocular)
    // Esto asegura que el seguimiento funcione incluso sin mostrar la vista
    Box(modifier = Modifier.size(0.dp)) {
        CameraPreviewView(
            enableSmoothing = true,  // Suavizado para juegos
            onPupilPositionDetected = { pupilX, pupilY ->
                viewModel.updatePupilPosition(pupilX, pupilY)
            }
        )
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF1a1a2e),
                        Color(0xFF0f3460)
                    )
                )
            )
    ) {
        Column(
            modifier = Modifier.fillMaxSize()
        ) {
            // Top Bar
            SnakeTopBar(
                score = gameState.score,
                isPaused = gameState.isPaused,
                onBack = onBack,
                onToggleCamera = { showEyeGestures = !showEyeGestures },
                onTogglePause = { viewModel.togglePause() }
            )
            
            // Vista de cámara para Eye Gestures (opcional)
            if (showEyeGestures && gameState.gameStarted && !gameState.gameOver) {
                SnakeEyeGesturesView(
                    onBlinkDetected = {
                        // Conectar parpadeo con ViewModel
                        viewModel.onBlinkDetected()
                    },
                    onPupilPositionUpdated = { pupilX, pupilY ->
                        // TODO: Conectar con tu detector de OpenCV
                        // Cuando tengas OpenCV funcionando, llama a:
                        viewModel.updatePupilPosition(pupilX, pupilY)
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(0.2f)
                )
            }
            
            // Canvas del juego Snake
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(if (showEyeGestures) 0.55f else 0.65f)
                    .padding(16.dp),
                contentAlignment = Alignment.Center
            ) {
                SnakeCanvasWithState(
                    gameState = gameState,
                    modifier = Modifier
                        .fillMaxSize()
                        .aspectRatio(1f)
                )
                
                // Overlay de game over
                if (gameState.gameOver) {
                    SnakeGameOverOverlay(
                        score = gameState.score,
                        onRestart = { viewModel.restart() }
                    )
                }
                
                // Overlay de inicio
                if (!gameState.gameStarted) {
                    SnakeStartOverlay(
                        onStart = { viewModel.start() }
                    )
                }
            }
            
            // Controles de dirección
            SnakeControls(
                onChangeDirection = { direction ->
                    viewModel.changeDirection(direction)
                },
                enabled = gameState.gameStarted && !gameState.gameOver,
                currentDirection = "Centro", // TODO: Conectar con pupil tracking
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(0.25f)
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            )
        }
        
        // Cursor de mirada superpuesto sobre TODO (fuera del Column)
        // Mostrar SIEMPRE que esté calibrado (incluso antes de iniciar juego)
        // Esto permite al usuario verificar que la calibración funciona
        if (isCalibrated) {
            GazeCursor(
                gazePosition = gazePosition,
                isVisible = true
            )
        }
    }
}

/**
 * Top Bar del juego Snake
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SnakeTopBar(
    score: Int,
    isPaused: Boolean,
    onBack: () -> Unit,
    onToggleCamera: () -> Unit,
    onTogglePause: () -> Unit
) {
    TopAppBar(
        title = {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "🐍",
                    fontSize = 24.sp
                )
                Column {
                    Text(
                        text = "SNAKE",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Puntuación: $score",
                        fontSize = 12.sp,
                        color = Color.White.copy(alpha = 0.7f)
                    )
                }
            }
        },
        navigationIcon = {
            IconButton(onClick = onBack) {
                Icon(Icons.Default.ArrowBack, "Volver", tint = Color.White)
            }
        },
        actions = {
            // Botón de pausa
            IconButton(onClick = onTogglePause) {
                Icon(
                    if (isPaused) Icons.Default.PlayArrow else Icons.Default.Pause,
                    if (isPaused) "Reanudar" else "Pausar",
                    tint = Color.White
                )
            }
            // Botón de cámara
            IconButton(onClick = onToggleCamera) {
                Icon(
                    Icons.Default.RemoveRedEye,
                    "Toggle Camera",
                    tint = Color.White.copy(alpha = 0.8f)
                )
            }
        },
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = Color(0xFF16213e)
        )
    )
}

/**
 * Vista de cámara para Eye Gestures con conexión a ViewModel
 * Conecta detección de pupila (OpenCV) con el ViewModel
 */
@Composable
fun SnakeEyeGesturesView(
    onBlinkDetected: () -> Unit,
    onPupilPositionUpdated: (Float, Float) -> Unit = { _, _ -> },
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier.background(Color(0xFF0f3460))
    ) {
        CameraPreviewView(
            onPupilPositionDetected = { pupilX, pupilY ->
                // ✅ Conectar detección de pupila con ViewModel
                onPupilPositionUpdated(pupilX, pupilY)
            }
        )
        
        // TODO: Agregar aquí tu capa de OpenCV para detección de pupila
        // Ejemplo:
        // PupilDetectorOverlay(
        //     onPupilDetected = { pupilX, pupilY ->
        //         onPupilPositionUpdated(pupilX, pupilY)
        //     }
        // )
        
        // Overlay con indicación
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0x33000000))
                .padding(8.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "Control por Pupila Calibrado\n(Requiere calibración previa)",
                color = Color.White,
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
        }
    }
}

/**
 * Canvas que dibuja la serpiente y la comida usando estado del ViewModel
 */
@Composable
fun SnakeCanvasWithState(
    gameState: SnakeGameUiState,
    modifier: Modifier = Modifier
) {
    val time by produceState(0L) {
        while (true) {
            value = System.currentTimeMillis()
            delay(16)
        }
    }
    
    Canvas(
        modifier = modifier.background(Color(0xFF1a1a2e))
    ) {
        // Calcular tamaño de celda basado en el tamaño real del Canvas
        // El juego usa 20 celdas fijas (gridSize = 20 en SnakeGame)
        val gridCells = 20
        val cellSize = minOf(size.width, size.height) / gridCells
        
        // Calcular número de columnas y filas visibles
        val cols = (size.width / cellSize).toInt()
        val rows = (size.height / cellSize).toInt()
        
        // Dibujar grid sutil
        drawSnakeGrid(cols, rows, cellSize)
        
        // Dibujar comida con efecto pulsante
        drawSnakeFood(gameState.food, cellSize, time)
        
        // Dibujar serpiente
        drawSnakeBody(
            snake = gameState.snake,
            direction = gameState.direction,
            cellSize = cellSize
        )
    }
}

/**
 * Dibujar grid del juego
 */
private fun DrawScope.drawSnakeGrid(cols: Int, rows: Int, cellSize: Float) {
    val gridColor = Color(0xFF16213e)
    
    for (i in 0 until cols) {
        drawLine(
            color = gridColor,
            start = Offset(i * cellSize, 0f),
            end = Offset(i * cellSize, size.height),
            strokeWidth = 1f
        )
    }
    
    for (i in 0 until rows) {
        drawLine(
            color = gridColor,
            start = Offset(0f, i * cellSize),
            end = Offset(size.width, i * cellSize),
            strokeWidth = 1f
        )
    }
}

/**
 * Dibujar comida con efecto pulsante
 */
private fun DrawScope.drawSnakeFood(food: GridPosition, cellSize: Float, time: Long) {
    val foodX = food.x * cellSize
    val foodY = food.y * cellSize
    
    val pulse = sin(time / 200.0) * 2 + 2
    
    drawCircle(
        color = Color(0xFFff5757),
        radius = cellSize / 2 - 2 + pulse.toFloat(),
        center = Offset(
            foodX + cellSize / 2,
            foodY + cellSize / 2
        )
    )
}

/**
 * Dibujar la serpiente completa
 */
private fun DrawScope.drawSnakeBody(
    snake: List<GridPosition>,
    direction: Direction,
    cellSize: Float
) {
    snake.forEachIndexed { index, segment ->
        val x = segment.x * cellSize
        val y = segment.y * cellSize
        
        if (index == 0) {
            // Cabeza
            drawRect(
                color = Color(0xFF4CAF50),
                topLeft = Offset(x + 1, y + 1),
                size = Size(cellSize - 2, cellSize - 2)
            )
            
            // Ojos según dirección
            drawSnakeEyes(x, y, cellSize, direction)
        } else {
            // Cuerpo con gradiente
            val alpha = 1f - (index.toFloat() / snake.size) * 0.5f
            drawRect(
                color = Color(0xFF4CAF50).copy(alpha = alpha),
                topLeft = Offset(x + 2, y + 2),
                size = Size(cellSize - 4, cellSize - 4)
            )
        }
    }
}

/**
 * Dibujar ojos de la serpiente según dirección
 */
private fun DrawScope.drawSnakeEyes(x: Float, y: Float, cellSize: Float, direction: Direction) {
    val eyeColor = Color.White
    val eyeSize = 3f
    val eyeOffset = 5f
    
    when {
        direction.x == 1 -> { // Derecha
            drawRect(eyeColor, Offset(x + cellSize - eyeOffset, y + eyeOffset), Size(eyeSize, eyeSize))
            drawRect(eyeColor, Offset(x + cellSize - eyeOffset, y + cellSize - eyeOffset - eyeSize), Size(eyeSize, eyeSize))
        }
        direction.x == -1 -> { // Izquierda
            drawRect(eyeColor, Offset(x + eyeOffset - eyeSize, y + eyeOffset), Size(eyeSize, eyeSize))
            drawRect(eyeColor, Offset(x + eyeOffset - eyeSize, y + cellSize - eyeOffset - eyeSize), Size(eyeSize, eyeSize))
        }
        direction.y == 1 -> { // Abajo
            drawRect(eyeColor, Offset(x + eyeOffset, y + cellSize - eyeOffset), Size(eyeSize, eyeSize))
            drawRect(eyeColor, Offset(x + cellSize - eyeOffset - eyeSize, y + cellSize - eyeOffset), Size(eyeSize, eyeSize))
        }
        else -> { // Arriba
            drawRect(eyeColor, Offset(x + eyeOffset, y + eyeOffset - eyeSize), Size(eyeSize, eyeSize))
            drawRect(eyeColor, Offset(x + cellSize - eyeOffset - eyeSize, y + eyeOffset - eyeSize), Size(eyeSize, eyeSize))
        }
    }
}

/**
 * Dibujar indicador de mirada
 */
private fun DrawScope.drawGazeIndicator(gazePosition: Offset) {
    drawCircle(
        color = Color(0xFFffd700).copy(alpha = 0.5f),
        radius = 15f,
        center = gazePosition,
        style = Stroke(width = 2f)
    )
}

/**
 * Controles direccionales para Snake
 * Incluye 4 botones en disposición de cruz
 */
@Composable
fun SnakeControls(
    onChangeDirection: (GameDirection) -> Unit,
    enabled: Boolean,
    currentDirection: String,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier.padding(8.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            // Botón Arriba
            SnakeControlButton(
                icon = Icons.Default.KeyboardArrowUp,
                label = "Arriba",
                onClick = { onChangeDirection(GameDirection.UP) },
                enabled = enabled,
                isActive = currentDirection == "Arriba"
            )
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(4.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Botón Izquierda
                SnakeControlButton(
                    icon = Icons.Default.KeyboardArrowLeft,
                    label = "Izq",
                    onClick = { onChangeDirection(GameDirection.LEFT) },
                    enabled = enabled,
                    isActive = currentDirection == "Izquierda"
                )
                
                // Centro (indicador)
                Surface(
                    modifier = Modifier.size(50.dp),
                    shape = CircleShape,
                    color = Color.Transparent
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Text(
                            text = when (currentDirection) {
                                "Arriba" -> "↑"
                                "Abajo" -> "↓"
                                "Izquierda" -> "←"
                                "Derecha" -> "→"
                                else -> "🐍"
                            },
                            fontSize = 24.sp,
                            color = Color.White.copy(alpha = 0.5f)
                        )
                    }
                }
                
                // Botón Derecha
                SnakeControlButton(
                    icon = Icons.Default.KeyboardArrowRight,
                    label = "Der",
                    onClick = { onChangeDirection(GameDirection.RIGHT) },
                    enabled = enabled,
                    isActive = currentDirection == "Derecha"
                )
            }
            
            // Botón Abajo
            SnakeControlButton(
                icon = Icons.Default.KeyboardArrowDown,
                label = "Abajo",
                onClick = { onChangeDirection(GameDirection.DOWN) },
                enabled = enabled,
                isActive = currentDirection == "Abajo"
            )
        }
    }
}

/**
 * Botón de control individual para Snake
 */
@Composable
fun SnakeControlButton(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    onClick: () -> Unit,
    enabled: Boolean,
    isActive: Boolean = false
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        colors = ButtonDefaults.buttonColors(
            containerColor = if (isActive) Color(0xFF4CAF50) else Color(0xFF2196F3),
            disabledContainerColor = Color(0xFF37474F)
        ),
        shape = CircleShape,
        modifier = Modifier.size(50.dp),
        contentPadding = PaddingValues(0.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            modifier = Modifier.size(24.dp),
            tint = Color.White
        )
    }
}

/**
 * Overlay de inicio del juego
 */
@Composable
fun SnakeStartOverlay(onStart: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xAA000000)),
        contentAlignment = Alignment.Center
    ) {
        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF16213e))
        ) {
            Column(
                modifier = Modifier.padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text("🐍", fontSize = 64.sp)
                Text(
                    "SNAKE",
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Text(
                    "Come y crece sin chocar",
                    fontSize = 14.sp,
                    color = Color.White.copy(alpha = 0.7f)
                )
                Button(
                    onClick = onStart,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF4CAF50)
                    )
                ) {
                    Text("Iniciar")
                }
            }
        }
    }
}

/**
 * Overlay de game over
 */
@Composable
fun SnakeGameOverOverlay(
    score: Int,
    onRestart: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xAA000000)),
        contentAlignment = Alignment.Center
    ) {
        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF16213e))
        ) {
            Column(
                modifier = Modifier.padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text("💥", fontSize = 48.sp)
                Text(
                    "GAME OVER",
                    fontSize = 32.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFff5757)
                )
                Text(
                    "Puntuación Final",
                    fontSize = 14.sp,
                    color = Color.White.copy(alpha = 0.7f)
                )
                Text(
                    score.toString(),
                    fontSize = 48.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFFFD700)
                )
                Button(
                    onClick = onRestart,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF4CAF50)
                    )
                ) {
                    Text("Reiniciar")
                }
                Text(
                    "O parpadea para reiniciar",
                    fontSize = 12.sp,
                    color = Color.White.copy(alpha = 0.5f)
                )
            }
        }
    }
}
