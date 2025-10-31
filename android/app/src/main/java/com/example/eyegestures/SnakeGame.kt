package com.example.eyegestures

import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.unit.IntSize
import kotlin.math.abs
import kotlin.math.floor

/**
 * Data class para representar una posición en la cuadrícula
 */
data class GridPosition(
    val x: Int,
    val y: Int
)

/**
 * Data class para representar la dirección de movimiento
 */
data class Direction(
    val x: Int,
    val y: Int
) {
    companion object {
        val RIGHT = Direction(1, 0)
        val LEFT = Direction(-1, 0)
        val UP = Direction(0, -1)
        val DOWN = Direction(0, 1)
        val NONE = Direction(0, 0)
    }
}

/**
 * Data class para el estado del juego
 */
data class GameState(
    val score: Int = 0,
    val gameOver: Boolean = false,
    val running: Boolean = false
)

/**
 * Juego Snake controlado por la mirada - Versión Kotlin
 * Traducido desde EyeSnake JavaScript
 */
class SnakeGame(
    private val canvasWidth: Float,
    private val canvasHeight: Float,
    private val onScoreChanged: (Int) -> Unit = {},
    private val onGameOver: (Int) -> Unit = {}
) {
    // Configuración del juego
    // gridCells = número de celdas en el tablero (20x20)
    // NO confundir con tamaño en pixels de cada celda
    private val gridCells = 20
    val gridSize = minOf(canvasWidth, canvasHeight) / gridCells  // Tamaño de celda en pixels
    val cols = gridCells  // Siempre 20 columnas
    val rows = gridCells  // Siempre 20 filas
    
    // Estado del juego
    var score = 0
        private set
    var gameOver = false
        private set
    var running = false
        private set
    
    // Cursor de mirada para dirección
    var gazePosition = Offset(canvasWidth / 2, canvasHeight / 2)
        private set
    
    // Serpiente (lista de posiciones)
    private var snake = mutableListOf<GridPosition>()
    
    // Direcciones
    private var direction = Direction.RIGHT
    private var nextDirection = Direction.RIGHT
    
    // Comida
    private var food = GridPosition(0, 0)
    
    // Tiempo
    private var lastMoveTime = System.currentTimeMillis()
    var moveInterval = 150L // ms entre movimientos
        private set
    
    init {
        initGame()
    }
    
    /**
     * Inicializar el juego
     * Traduce: init()
     */
    private fun initGame() {
        // Inicializar serpiente en el centro
        val centerX = cols / 2
        val centerY = rows / 2
        
        snake = mutableListOf(
            GridPosition(centerX, centerY),
            GridPosition(centerX - 1, centerY),
            GridPosition(centerX - 2, centerY)
        )
        
        spawnFood()
    }
    
    /**
     * Generar comida en una posición aleatoria válida
     * Traduce: spawnFood()
     */
    private fun spawnFood() {
        var validPosition = false
        
        while (!validPosition) {
            food = GridPosition(
                x = (0 until cols).random(),
                y = (0 until rows).random()
            )
            
            // Verificar que no esté en la serpiente
            validPosition = snake.none { segment ->
                segment.x == food.x && segment.y == food.y
            }
        }
    }
    
    /**
     * Actualizar posición de la mirada y calcular dirección
     * Traduce: onGaze(x, y)
     */
    fun updateGazePosition(x: Float, y: Float) {
        gazePosition = Offset(x, y)
        
        // Calcular dirección basada en la posición de la mirada
        val head = snake.firstOrNull() ?: return
        val headPixelX = head.x * gridSize + gridSize / 2f
        val headPixelY = head.y * gridSize + gridSize / 2f
        
        val dx = gazePosition.x - headPixelX
        val dy = gazePosition.y - headPixelY
        
        // Determinar dirección predominante
        if (abs(dx) > abs(dy)) {
            // Movimiento horizontal
            nextDirection = when {
                dx > 0 && direction.x != -1 -> Direction.RIGHT
                dx < 0 && direction.x != 1 -> Direction.LEFT
                else -> nextDirection
            }
        } else {
            // Movimiento vertical
            nextDirection = when {
                dy > 0 && direction.y != -1 -> Direction.DOWN
                dy < 0 && direction.y != 1 -> Direction.UP
                else -> nextDirection
            }
        }
    }
    
    /**
     * Actualizar dirección desde ML Kit (usando ángulos de Euler)
     * Método adicional para integración con GazeDirectionDetector
     */
    fun updateDirectionFromGaze(gazeDirection: GameDirection) {
        nextDirection = when (gazeDirection) {
            GameDirection.UP -> if (direction.y != 1) Direction.UP else nextDirection
            GameDirection.DOWN -> if (direction.y != -1) Direction.DOWN else nextDirection
            GameDirection.LEFT -> if (direction.x != 1) Direction.LEFT else nextDirection
            GameDirection.RIGHT -> if (direction.x != -1) Direction.RIGHT else nextDirection
            GameDirection.NONE -> nextDirection
        }
    }
    
    /**
     * Actualizar el estado del juego
     * Traduce: update()
     */
    fun updateGame(): Boolean {
        if (gameOver) return false
        
        val now = System.currentTimeMillis()
        if (now - lastMoveTime < moveInterval) return false
        
        lastMoveTime = now
        
        // Actualizar dirección
        direction = nextDirection.copy()
        
        // Calcular nueva posición de la cabeza
        val head = snake.first()
        var newHead = GridPosition(
            x = head.x + direction.x,
            y = head.y + direction.y
        )
        
        // Verificar colisión con bordes (wrap around)
        newHead = wrapAroundBorders(newHead)
        
        // Verificar colisión con sí misma
        if (checkSelfCollision(newHead)) {
            gameOver = true
            onGameOver(score)
            return false
        }
        
        // Añadir nueva cabeza
        snake.add(0, newHead)
        
        // Verificar si comió
        if (newHead.x == food.x && newHead.y == food.y) {
            score += 10
            onScoreChanged(score)
            spawnFood()
            
            // Aumentar velocidad ligeramente
            moveInterval = maxOf(50L, moveInterval - 2)
        } else {
            // Quitar cola si no comió
            snake.removeLastOrNull()
        }
        
        return true
    }
    
    /**
     * Envolver coordenadas en los bordes (teletransporte)
     */
    private fun wrapAroundBorders(position: GridPosition): GridPosition {
        var x = position.x
        var y = position.y
        
        if (x < 0) x = cols - 1
        if (x >= cols) x = 0
        if (y < 0) y = rows - 1
        if (y >= rows) y = 0
        
        return GridPosition(x, y)
    }
    
    /**
     * Verificar colisión con sí misma
     * Traduce: parte de update() que verifica colisión
     */
    private fun checkSelfCollision(newHead: GridPosition): Boolean {
        return snake.any { segment ->
            segment.x == newHead.x && segment.y == newHead.y
        }
    }
    
    /**
     * Verificar colisión con los bordes (sin wrap around)
     * Método alternativo si no quieres teletransporte
     */
    private fun checkBorderCollision(position: GridPosition): Boolean {
        return position.x < 0 || position.x >= cols ||
               position.y < 0 || position.y >= rows
    }
    
    /**
     * Obtener la serpiente completa
     */
    fun getSnake(): List<GridPosition> = snake.toList()
    
    /**
     * Obtener la posición de la comida
     */
    fun getFood(): GridPosition = food
    
    /**
     * Obtener el estado actual del juego
     */
    fun getGameState(): GameState {
        return GameState(
            score = score,
            gameOver = gameOver,
            running = running
        )
    }
    
    /**
     * Obtener la dirección actual
     */
    fun getCurrentDirection(): Direction = direction
    
    /**
     * Iniciar el juego
     * Traduce: start()
     */
    fun start() {
        running = true
    }
    
    /**
     * Detener el juego
     * Traduce: stop()
     */
    fun stop() {
        running = false
    }
    
    /**
     * Reiniciar el juego
     */
    fun restart() {
        score = 0
        gameOver = false
        running = false
        direction = Direction.RIGHT
        nextDirection = Direction.RIGHT
        lastMoveTime = System.currentTimeMillis()
        moveInterval = 150L
        gazePosition = Offset(canvasWidth / 2, canvasHeight / 2)
        
        initGame()
    }
    
    /**
     * Destruir el juego
     * Traduce: destroy()
     */
    fun destroy() {
        stop()
        snake.clear()
    }
    
    /**
     * Obtener información de debug
     */
    fun getDebugInfo(): String {
        return """
            Score: $score
            Snake Length: ${snake.size}
            Direction: (${direction.x}, ${direction.y})
            Food: (${food.x}, ${food.y})
            Head: (${snake.firstOrNull()?.x}, ${snake.firstOrNull()?.y})
            Game Over: $gameOver
            Running: $running
        """.trimIndent()
    }
}
