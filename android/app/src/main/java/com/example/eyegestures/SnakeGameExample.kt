package com.example.eyegestures

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay

/**
 * Ejemplo de integración de Eye Gestures con el juego Snake
 * Controla la serpiente usando la dirección de la mirada
 */
@Composable
fun SnakeGameWithEyeGestures() {
    var currentDirection by remember { mutableStateOf(GameDirection.RIGHT) }
    var score by remember { mutableStateOf(0) }
    
    Column(modifier = Modifier.fillMaxSize()) {
        // Vista de cámara con detector de pupila
        Box(
            modifier = Modifier
                .weight(0.3f)
                .fillMaxWidth()
        ) {
            CameraPreviewView(
                onPupilPositionDetected = { _, _ ->
                    // TODO: Convertir posición de pupila a dirección
                }
            )
        }
        
        // Canvas del juego Snake
        Box(
            modifier = Modifier
                .weight(0.6f)
                .fillMaxWidth()
                .background(Color(0xFF1E1E1E))
        ) {
            SnakeGameCanvas(
                direction = currentDirection,
                onScoreChanged = { newScore -> score = newScore }
            )
        }
        
        // Información del juego
        Box(
            modifier = Modifier
                .weight(0.1f)
                .fillMaxWidth()
                .background(Color(0xFF2D2D2D)),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "Puntuación: $score | Dirección: ${currentDirection.name}",
                color = Color.White
            )
        }
    }
}

@Composable
fun SnakeGameCanvas(
    direction: GameDirection,
    onScoreChanged: (Int) -> Unit
) {
    // Implementación simplificada del juego Snake
    var snake by remember { 
        mutableStateOf(listOf(Offset(10f, 10f), Offset(9f, 10f), Offset(8f, 10f))) 
    }
    var food by remember { mutableStateOf(Offset(15f, 15f)) }
    
    LaunchedEffect(direction) {
        while (true) {
            delay(150) // Velocidad del juego
            
            // Mover la serpiente según la dirección
            val head = snake.first()
            val newHead = when (direction) {
                GameDirection.UP -> Offset(head.x, head.y - 1)
                GameDirection.DOWN -> Offset(head.x, head.y + 1)
                GameDirection.LEFT -> Offset(head.x - 1, head.y)
                GameDirection.RIGHT -> Offset(head.x + 1, head.y)
                GameDirection.NONE -> head
            }
            
            // Actualizar serpiente
            snake = listOf(newHead) + snake.dropLast(1)
            
            // Verificar si come la comida
            if (newHead == food) {
                snake = listOf(newHead) + snake
                food = Offset(
                    (0..20).random().toFloat(),
                    (0..20).random().toFloat()
                )
                onScoreChanged(snake.size - 3)
            }
        }
    }
    
    Canvas(modifier = Modifier.fillMaxSize()) {
        val cellSize = size.width / 20
        
        // Dibujar serpiente
        snake.forEach { segment ->
            drawCircle(
                color = Color.Green,
                radius = cellSize / 2,
                center = Offset(
                    segment.x * cellSize + cellSize / 2,
                    segment.y * cellSize + cellSize / 2
                )
            )
        }
        
        // Dibujar comida
        drawCircle(
            color = Color.Red,
            radius = cellSize / 2,
            center = Offset(
                food.x * cellSize + cellSize / 2,
                food.y * cellSize + cellSize / 2
            )
        )
    }
}
