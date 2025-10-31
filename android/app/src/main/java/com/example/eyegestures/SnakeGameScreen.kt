package com.example.eyegestures

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlin.math.sin

/**
 * Pantalla completa del juego Snake con Eye Gestures
 * Integra la lógica de SnakeGame.kt con la UI de Compose
 */
@Composable
fun SnakeGameScreen() {
    val density = LocalDensity.current
    val canvasWidth = with(density) { (LocalDensity.current.density * 360).dp.toPx() }
    val canvasHeight = with(density) { (LocalDensity.current.density * 500).dp.toPx() }
    
    var score by remember { mutableStateOf(0) }
    var gameOver by remember { mutableStateOf(false) }
    var gameStarted by remember { mutableStateOf(false) }
    
    val snakeGame = remember {
        SnakeGame(
            canvasWidth = canvasWidth,
            canvasHeight = canvasHeight,
            onScoreChanged = { newScore -> score = newScore },
            onGameOver = { finalScore ->
                gameOver = true
                score = finalScore
            }
        )
    }
    
    // Game loop
    LaunchedEffect(gameStarted) {
        if (gameStarted && !gameOver) {
            while (gameStarted && !gameOver) {
                snakeGame.updateGame()
                delay(16) // ~60 FPS
            }
        }
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF1a1a2e))
    ) {
        // Header con puntuación
        GameHeader(
            score = score,
            gazeDirection = "Centro", // TODO: Conectar con pupil tracking
            modifier = Modifier.fillMaxWidth()
        )
        
        // Vista de cámara (detector de pupila)
        // TODO: Conectar con sistema de pupil tracking
        Box(
            modifier = Modifier
                .weight(0.3f)
                .fillMaxWidth()
        ) {
            CameraPreviewView(
                onPupilPositionDetected = { _, _ ->
                    // TODO: Convertir posición de pupila a dirección del juego
                }
            )
            
            // Overlay con instrucciones
            if (!gameStarted) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color(0xAA000000)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "Parpadea para comenzar",
                        color = Color.White,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
        
        // Canvas del juego
        Box(
            modifier = Modifier
                .weight(0.6f)
                .fillMaxWidth()
                .background(Color(0xFF0f3460))
        ) {
            SnakeGameCanvas(
                snakeGame = snakeGame,
                modifier = Modifier.fillMaxSize()
            )
            
            // Game Over overlay
            if (gameOver) {
                GameOverOverlay(
                    score = score,
                    onRestart = {
                        snakeGame.restart()
                        gameOver = false
                        score = 0
                        gameStarted = true
                    },
                    modifier = Modifier.fillMaxSize()
                )
            }
        }
        
        // Botones de control
        GameControls(
            gameStarted = gameStarted,
            gameOver = gameOver,
            onStart = {
                snakeGame.start()
                gameStarted = true
            },
            onRestart = {
                snakeGame.restart()
                gameOver = false
                score = 0
                gameStarted = true
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        )
    }
}

@Composable
fun GameHeader(
    score: Int,
    gazeDirection: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.padding(16.dp),
        colors = CardDefaults.cardElevation(defaultElevation = 4.dp).let {
            CardDefaults.cardColors(containerColor = Color(0xFF16213e))
        }
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "SNAKE",
                    color = Color(0xFF4CAF50),
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Eye Gestures",
                    color = Color.White,
                    fontSize = 12.sp
                )
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = "Puntuación",
                    color = Color.White.copy(alpha = 0.7f),
                    fontSize = 12.sp
                )
                Text(
                    text = score.toString(),
                    color = Color(0xFFffd700),
                    fontSize = 32.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = "Dirección",
                    color = Color.White.copy(alpha = 0.7f),
                    fontSize = 12.sp
                )
                Text(
                    text = gazeDirection,
                    color = Color(0xFF00d4ff),
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
fun SnakeGameCanvas(
    snakeGame: SnakeGame,
    modifier: Modifier = Modifier
) {
    val time by produceState(0L) {
        while (true) {
            value = System.currentTimeMillis()
            delay(16)
        }
    }
    
    Canvas(modifier = modifier) {
        val cellSize = snakeGame.gridSize.toFloat()
        
        // Dibujar grid sutil
        drawGrid(snakeGame.cols, snakeGame.rows, cellSize)
        
        // Dibujar comida con efecto pulsante
        drawFood(snakeGame.getFood(), cellSize, time)
        
        // Dibujar serpiente
        drawSnake(snakeGame.getSnake(), snakeGame.getCurrentDirection(), cellSize)
        
        // Dibujar indicador de mirada
        drawGazeIndicator(snakeGame.gazePosition)
        
        // Línea de guía de la cabeza a la mirada
        drawGuideLine(snakeGame.getSnake().firstOrNull(), snakeGame.gazePosition, cellSize)
    }
}

private fun DrawScope.drawGrid(cols: Int, rows: Int, cellSize: Float) {
    val gridColor = Color(0xFF16213e)
    
    // Líneas verticales
    for (i in 0 until cols) {
        drawLine(
            color = gridColor,
            start = Offset(i * cellSize, 0f),
            end = Offset(i * cellSize, size.height),
            strokeWidth = 1f
        )
    }
    
    // Líneas horizontales
    for (i in 0 until rows) {
        drawLine(
            color = gridColor,
            start = Offset(0f, i * cellSize),
            end = Offset(size.width, i * cellSize),
            strokeWidth = 1f
        )
    }
}

private fun DrawScope.drawFood(food: GridPosition, cellSize: Float, time: Long) {
    val foodX = food.x * cellSize
    val foodY = food.y * cellSize
    
    // Efecto pulsante
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

private fun DrawScope.drawSnake(
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
                size = androidx.compose.ui.geometry.Size(cellSize - 2, cellSize - 2)
            )
            
            // Ojos
            drawSnakeEyes(x, y, cellSize, direction)
        } else {
            // Cuerpo con gradiente
            val alpha = 1f - (index.toFloat() / snake.size) * 0.5f
            drawRect(
                color = Color(0xFF4CAF50).copy(alpha = alpha),
                topLeft = Offset(x + 2, y + 2),
                size = androidx.compose.ui.geometry.Size(cellSize - 4, cellSize - 4)
            )
        }
    }
}

private fun DrawScope.drawSnakeEyes(x: Float, y: Float, cellSize: Float, direction: Direction) {
    val eyeColor = Color.White
    val eyeSize = 3f
    val eyeOffset = 5f
    
    when {
        direction.x == 1 -> { // Derecha
            drawRect(eyeColor, Offset(x + cellSize - eyeOffset, y + eyeOffset), androidx.compose.ui.geometry.Size(eyeSize, eyeSize))
            drawRect(eyeColor, Offset(x + cellSize - eyeOffset, y + cellSize - eyeOffset - eyeSize), androidx.compose.ui.geometry.Size(eyeSize, eyeSize))
        }
        direction.x == -1 -> { // Izquierda
            drawRect(eyeColor, Offset(x + eyeOffset - eyeSize, y + eyeOffset), androidx.compose.ui.geometry.Size(eyeSize, eyeSize))
            drawRect(eyeColor, Offset(x + eyeOffset - eyeSize, y + cellSize - eyeOffset - eyeSize), androidx.compose.ui.geometry.Size(eyeSize, eyeSize))
        }
        direction.y == 1 -> { // Abajo
            drawRect(eyeColor, Offset(x + eyeOffset, y + cellSize - eyeOffset), androidx.compose.ui.geometry.Size(eyeSize, eyeSize))
            drawRect(eyeColor, Offset(x + cellSize - eyeOffset - eyeSize, y + cellSize - eyeOffset), androidx.compose.ui.geometry.Size(eyeSize, eyeSize))
        }
        else -> { // Arriba
            drawRect(eyeColor, Offset(x + eyeOffset, y + eyeOffset - eyeSize), androidx.compose.ui.geometry.Size(eyeSize, eyeSize))
            drawRect(eyeColor, Offset(x + cellSize - eyeOffset - eyeSize, y + eyeOffset - eyeSize), androidx.compose.ui.geometry.Size(eyeSize, eyeSize))
        }
    }
}

private fun DrawScope.drawGazeIndicator(gazePosition: Offset) {
    drawCircle(
        color = Color(0xFFffd700).copy(alpha = 0.5f),
        radius = 15f,
        center = gazePosition,
        style = Stroke(width = 2f)
    )
}

private fun DrawScope.drawGuideLine(
    head: GridPosition?,
    gazePosition: Offset,
    cellSize: Float
) {
    if (head == null) return
    
    val headPixelX = head.x * cellSize + cellSize / 2
    val headPixelY = head.y * cellSize + cellSize / 2
    
    drawLine(
        color = Color(0xFFffd700).copy(alpha = 0.3f),
        start = Offset(headPixelX, headPixelY),
        end = gazePosition,
        strokeWidth = 1f,
        pathEffect = PathEffect.dashPathEffect(floatArrayOf(5f, 5f))
    )
}

@Composable
fun GameOverOverlay(
    score: Int,
    onRestart: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier.background(Color(0xAA000000)),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "GAME OVER",
                color = Color(0xFFff5757),
                fontSize = 48.sp,
                fontWeight = FontWeight.Bold
            )
            
            Text(
                text = "Puntuación Final: $score",
                color = Color.White,
                fontSize = 24.sp
            )
            
            Button(
                onClick = onRestart,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF4CAF50)
                )
            ) {
                Text("Reiniciar", fontSize = 18.sp)
            }
            
            Text(
                text = "O parpadea para reiniciar",
                color = Color.White.copy(alpha = 0.7f),
                fontSize = 14.sp
            )
        }
    }
}

@Composable
fun GameControls(
    gameStarted: Boolean,
    gameOver: Boolean,
    onStart: () -> Unit,
    onRestart: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.Center
    ) {
        if (!gameStarted || gameOver) {
            Button(
                onClick = if (gameOver) onRestart else onStart,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF4CAF50)
                )
            ) {
                Text(
                    text = if (gameOver) "Reiniciar" else "Iniciar",
                    fontSize = 18.sp
                )
            }
        }
    }
}
