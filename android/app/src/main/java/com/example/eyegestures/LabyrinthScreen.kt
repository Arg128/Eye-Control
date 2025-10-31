package com.example.eyegestures

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel

/**
 * Pantalla completa del juego de Laberinto con ViewModel
 * Versión actualizada con navegación y estado observable
 */
@Composable
fun LabyrinthScreen(
    onBack: () -> Unit = {},
    viewModel: MazeViewModel = viewModel()
) {
    // Observar estado del juego desde ViewModel
    val gameState by viewModel.gameState.collectAsState()
    
    var showEyeGestures by remember { mutableStateOf(true) }
    
    // Observar el cursor de mirada
    val isCalibrated by GazeCursorManager.isCalibrated.collectAsState()
    val gazePosition by GazeCursorManager.gazePosition.collectAsState()
    
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
        // Cámara invisible de fondo para seguimiento continuo
        Box(modifier = Modifier.size(0.dp)) {
            CameraPreviewView(
                enableSmoothing = true,
                onPupilPositionDetected = { pupilX, pupilY ->
                    viewModel.updatePupilPosition(pupilX, pupilY)
                }
            )
        }
        
        Column(
            modifier = Modifier.fillMaxSize()
        ) {
            // Top Bar
            LabyrinthTopBar(
                moves = gameState.moves,
                score = gameState.score,
                onBack = onBack,
                onToggleCamera = { showEyeGestures = !showEyeGestures }
            )
            
            // Vista de cámara para Eye Gestures
            if (showEyeGestures && gameState.gameStarted && !gameState.gameWon) {
                LabyrinthEyeGesturesView(
                    onBlinkDetected = {
                        viewModel.onBlinkDetected()
                    },
                    onPupilPositionUpdated = { pupilX, pupilY ->
                        // TODO: Conectar con tu detector de OpenCV
                        viewModel.updatePupilPosition(pupilX, pupilY)
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(0.25f)
                )
            }
            
            // Canvas del laberinto
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(if (showEyeGestures) 0.5f else 0.65f)
                    .padding(16.dp),
                contentAlignment = Alignment.Center
            ) {
                LabyrinthCanvasWithState(
                    gameState = gameState,
                    modifier = Modifier
                        .fillMaxSize()
                        .aspectRatio(1f)
                )
                
                // Overlay de victoria
                if (gameState.gameWon) {
                    LabyrinthWinOverlay(
                        score = gameState.score,
                        moves = gameState.moves,
                        onRestart = { viewModel.restart() }
                    )
                }
                
                // Overlay de inicio
                if (!gameState.gameStarted) {
                    LabyrinthStartOverlay(
                        onStart = { viewModel.start() }
                    )
                }
            }
            
            // Controles direccionales
            LabyrinthControls(
                onMoveUp = { viewModel.movePlayer(Direction.UP) },
                onMoveDown = { viewModel.movePlayer(Direction.DOWN) },
                onMoveLeft = { viewModel.movePlayer(Direction.LEFT) },
                onMoveRight = { viewModel.movePlayer(Direction.RIGHT) },
                enabled = gameState.gameStarted && !gameState.gameWon,
                currentDirection = "Centro", // TODO: Conectar con pupil tracking
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(0.25f)
            )
        }
        
        // Cursor de mirada superpuesto (mostrar siempre que esté calibrado)
        if (isCalibrated) {
            GazeCursor(
                gazePosition = gazePosition,
                isVisible = true
            )
        }
    }
}

/**
 * Top Bar del laberinto
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LabyrinthTopBar(
    moves: Int,
    score: Int,
    onBack: () -> Unit,
    onToggleCamera: () -> Unit
) {
    TopAppBar(
        title = {
            Column {
                Text(
                    "🧩 Laberinto",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Text(
                    "Movimientos: $moves | Puntos: $score",
                    fontSize = 12.sp,
                    color = Color.White.copy(alpha = 0.8f)
                )
            }
        },
        navigationIcon = {
            IconButton(onClick = onBack) {
                Icon(
                    Icons.Default.ArrowBack,
                    "Volver",
                    tint = Color.White
                )
            }
        },
        actions = {
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
 * Vista de cámara para Eye Gestures
 * Conecta detección de pupila con el ViewModel del laberinto
 */
@Composable
fun LabyrinthEyeGesturesView(
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
        
        // TODO: Agregar capa de OpenCV para detección de pupila
        
        // Overlay con indicación
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0x33000000))
                .padding(8.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "Control por Pupila Calibrado",
                color = Color.White,
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

/**
 * Canvas que dibuja el laberinto usando estado del ViewModel
 */
@Composable
fun LabyrinthCanvasWithState(
    gameState: MazeGameUiState,
    modifier: Modifier = Modifier
) {
    Canvas(
        modifier = modifier.background(Color(0xFF1a1a2e))
    ) {
        val gridSize = 10
        val cellSize = size.width / gridSize
        
        val maze = gameState.maze
        val playerPosition = gameState.playerPosition
        val goalPosition = gameState.goalPosition
        val path = gameState.path
        
        // Dibujar matriz del laberinto
        for (y in 0 until gridSize) {
            for (x in 0 until gridSize) {
                val isWall = maze[y][x] == 1
                val isPath = path.contains(GridPosition(x, y))
                
                drawLabyrinthCell(
                    x = x,
                    y = y,
                    cellSize = cellSize,
                    isWall = isWall,
                    isPath = isPath
                )
            }
        }
        
        // Dibujar meta (estrella pulsante)
        drawLabyrinthGoal(goalPosition, cellSize)
        
        // Dibujar jugador (cara sonriente)
        drawLabyrinthPlayer(playerPosition, cellSize)
    }
}

/**
 * Dibuja una celda del laberinto
 */
fun DrawScope.drawLabyrinthCell(
    x: Int,
    y: Int,
    cellSize: Float,
    isWall: Boolean,
    isPath: Boolean
) {
    val posX = x * cellSize
    val posY = y * cellSize
    
    when {
        isWall -> {
            // Pared con efecto 3D
            drawRoundRect(
                color = Color(0xFF2d4a6e),
                topLeft = Offset(posX + 1, posY + 1),
                size = Size(cellSize - 2, cellSize - 2),
                cornerRadius = CornerRadius(4f, 4f)
            )
            drawRoundRect(
                color = Color(0xFF1c2d47),
                topLeft = Offset(posX + 1, posY + 3),
                size = Size(cellSize - 2, cellSize - 4),
                cornerRadius = CornerRadius(4f, 4f)
            )
        }
        isPath -> {
            // Camino recorrido
            drawRoundRect(
                color = Color(0xFF16a085).copy(alpha = 0.3f),
                topLeft = Offset(posX + 2, posY + 2),
                size = Size(cellSize - 4, cellSize - 4),
                cornerRadius = CornerRadius(2f, 2f)
            )
        }
        else -> {
            // Celda vacía
            drawRect(
                color = Color(0xFF0a1929).copy(alpha = 0.5f),
                topLeft = Offset(posX, posY),
                size = Size(cellSize, cellSize)
            )
        }
    }
}

/**
 * Dibuja el jugador (cara sonriente azul)
 */
fun DrawScope.drawLabyrinthPlayer(position: GridPosition, cellSize: Float) {
    val centerX = position.x * cellSize + cellSize / 2
    val centerY = position.y * cellSize + cellSize / 2
    val radius = cellSize * 0.35f
    
    // Cara
    drawCircle(
        color = Color(0xFF3498db),
        radius = radius,
        center = Offset(centerX, centerY)
    )
    
    // Ojos
    drawCircle(
        color = Color.White,
        radius = radius * 0.2f,
        center = Offset(centerX - radius * 0.3f, centerY - radius * 0.2f)
    )
    drawCircle(
        color = Color.White,
        radius = radius * 0.2f,
        center = Offset(centerX + radius * 0.3f, centerY - radius * 0.2f)
    )
    
    // Pupilas
    drawCircle(
        color = Color.Black,
        radius = radius * 0.1f,
        center = Offset(centerX - radius * 0.3f, centerY - radius * 0.2f)
    )
    drawCircle(
        color = Color.Black,
        radius = radius * 0.1f,
        center = Offset(centerX + radius * 0.3f, centerY - radius * 0.2f)
    )
    
    // Sonrisa
    val smilePath = Path().apply {
        moveTo(centerX - radius * 0.4f, centerY + radius * 0.1f)
        quadraticBezierTo(
            centerX, centerY + radius * 0.5f,
            centerX + radius * 0.4f, centerY + radius * 0.1f
        )
    }
    drawPath(
        path = smilePath,
        color = Color.White,
        style = Stroke(width = radius * 0.15f)
    )
}

/**
 * Dibuja la meta (estrella dorada pulsante)
 */
fun DrawScope.drawLabyrinthGoal(position: GridPosition, cellSize: Float) {
    val centerX = position.x * cellSize + cellSize / 2
    val centerY = position.y * cellSize + cellSize / 2
    val outerRadius = cellSize * 0.4f
    val innerRadius = outerRadius * 0.4f
    
    // Estrella de 5 puntas
    val starPath = Path().apply {
        for (i in 0 until 10) {
            val angle = (i * 36 - 90) * Math.PI / 180
            val radius = if (i % 2 == 0) outerRadius else innerRadius
            val x = centerX + (radius * kotlin.math.cos(angle)).toFloat()
            val y = centerY + (radius * kotlin.math.sin(angle)).toFloat()
            
            if (i == 0) moveTo(x, y) else lineTo(x, y)
        }
        close()
    }
    
    drawPath(
        path = starPath,
        color = Color(0xFFf39c12)
    )
    
    // Brillo interior
    drawPath(
        path = starPath,
        color = Color(0xFFf1c40f),
        style = Stroke(width = 2f)
    )
}

/**
 * Controles direccionales
 */
@Composable
fun LabyrinthControls(
    onMoveUp: () -> Unit,
    onMoveDown: () -> Unit,
    onMoveLeft: () -> Unit,
    onMoveRight: () -> Unit,
    enabled: Boolean,
    currentDirection: String,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .padding(8.dp),
        contentAlignment = Alignment.Center
    ) {
        // Layout en cruz
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            // Arriba
            DirectionalButton(
                icon = Icons.Default.ArrowUpward,
                onClick = onMoveUp,
                enabled = enabled,
                isActive = currentDirection == "Arriba"
            )
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(4.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Izquierda
                DirectionalButton(
                    icon = Icons.Default.ArrowBack,
                    onClick = onMoveLeft,
                    enabled = enabled,
                    isActive = currentDirection == "Izquierda"
                )
                
                Spacer(modifier = Modifier.width(50.dp))
                
                // Derecha
                DirectionalButton(
                    icon = Icons.Default.ArrowForward,
                    onClick = onMoveRight,
                    enabled = enabled,
                    isActive = currentDirection == "Derecha"
                )
            }
            
            // Abajo
            DirectionalButton(
                icon = Icons.Default.ArrowDownward,
                onClick = onMoveDown,
                enabled = enabled,
                isActive = currentDirection == "Abajo"
            )
        }
    }
}

@Composable
fun DirectionalButton(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    onClick: () -> Unit,
    enabled: Boolean,
    isActive: Boolean
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        modifier = Modifier.size(50.dp),
        shape = CircleShape,
        colors = ButtonDefaults.buttonColors(
            containerColor = if (isActive) Color(0xFF16a085) else Color(0xFF2980b9),
            disabledContainerColor = Color(0xFF34495e)
        )
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(24.dp),
            tint = Color.White
        )
    }
}

/**
 * Overlay de victoria
 */
@Composable
fun LabyrinthWinOverlay(
    score: Int,
    moves: Int,
    onRestart: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black.copy(alpha = 0.8f)),
        contentAlignment = Alignment.Center
    ) {
        Card(
            modifier = Modifier.padding(32.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFF16213e)
            )
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    "🎉 ¡Victoria!",
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFf39c12)
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    "Puntuación: $score",
                    fontSize = 20.sp,
                    color = Color.White
                )
                Text(
                    "Movimientos: $moves",
                    fontSize = 16.sp,
                    color = Color.White.copy(alpha = 0.8f)
                )
                Spacer(modifier = Modifier.height(24.dp))
                Button(
                    onClick = onRestart,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF16a085)
                    )
                ) {
                    Text("Jugar de Nuevo")
                }
            }
        }
    }
}

/**
 * Overlay de inicio
 */
@Composable
fun LabyrinthStartOverlay(
    onStart: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black.copy(alpha = 0.7f)),
        contentAlignment = Alignment.Center
    ) {
        Card(
            modifier = Modifier.padding(32.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFF16213e)
            )
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    "🧩",
                    fontSize = 48.sp
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    "Laberinto",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    "Llega a la estrella",
                    fontSize = 14.sp,
                    color = Color.White.copy(alpha = 0.7f)
                )
                Spacer(modifier = Modifier.height(24.dp))
                Button(
                    onClick = onStart,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF2980b9)
                    )
                ) {
                    Text("Iniciar")
                }
            }
        }
    }
}
