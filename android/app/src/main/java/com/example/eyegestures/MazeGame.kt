package com.example.eyegestures

import androidx.compose.ui.geometry.Offset

/**
 * Data class para representar una celda en el laberinto
 */
data class MazeCell(
    val x: Int,
    val y: Int,
    val isWall: Boolean = false,
    val isVisited: Boolean = false
)

/**
 * Tipo de celda en el laberinto
 */
enum class CellType {
    EMPTY,      // Celda vacía (camino)
    WALL,       // Pared
    PLAYER,     // Jugador
    GOAL,       // Meta
    PATH        // Camino recorrido
}

/**
 * Estado del juego de laberinto
 */
data class MazeGameState(
    val playerPosition: GridPosition = GridPosition(0, 0),
    val goalPosition: GridPosition = GridPosition(9, 9),
    val score: Int = 0,
    val moves: Int = 0,
    val gameWon: Boolean = false,
    val gameStarted: Boolean = false
)

/**
 * Lógica del juego de Laberinto
 */
class MazeGame(
    val gridSize: Int = 10,
    private val onPositionChanged: (GridPosition) -> Unit = {},
    private val onGameWon: (Int, Int) -> Unit = { _, _ -> }
) {
    // Estado del juego
    private var playerPosition = GridPosition(0, 0)
    private var goalPosition = GridPosition(gridSize - 1, gridSize - 1)
    private var maze = Array(gridSize) { IntArray(gridSize) { 0 } }
    private var path = mutableListOf<GridPosition>()
    
    var moves = 0
        private set
    var score = 0
        private set
    var gameWon = false
        private set
    var gameStarted = false
        private set
    
    init {
        generateMaze()
    }
    
    /**
     * Generar un laberinto simple
     * 0 = camino, 1 = pared
     */
    private fun generateMaze() {
        // Inicializar todo como camino
        for (y in 0 until gridSize) {
            for (x in 0 until gridSize) {
                maze[y][x] = 0
            }
        }
        
        // Generar algunas paredes aleatorias (30% de probabilidad)
        for (y in 0 until gridSize) {
            for (x in 0 until gridSize) {
                // No poner paredes en inicio, meta, o sus alrededores
                if ((x == 0 && y == 0) || 
                    (x == gridSize - 1 && y == gridSize - 1) ||
                    (x <= 1 && y <= 1) ||
                    (x >= gridSize - 2 && y >= gridSize - 2)) {
                    maze[y][x] = 0
                } else if (Math.random() < 0.25) {
                    maze[y][x] = 1
                }
            }
        }
        
        // Asegurar que siempre hay un camino desde inicio a meta
        ensurePath()
    }
    
    /**
     * Asegurar que hay un camino del inicio a la meta
     */
    private fun ensurePath() {
        // Crear un camino simple en forma de escalera
        var x = 0
        var y = 0
        
        while (x < gridSize - 1 || y < gridSize - 1) {
            maze[y][x] = 0
            
            if (x < gridSize - 1 && (y == gridSize - 1 || Math.random() > 0.5)) {
                x++
            } else if (y < gridSize - 1) {
                y++
            }
            
            maze[y][x] = 0
        }
    }
    
    /**
     * Mover el jugador en una dirección
     */
    fun movePlayer(direction: Direction): Boolean {
        if (gameWon) return false
        
        val newX = playerPosition.x + direction.x
        val newY = playerPosition.y + direction.y
        
        // Verificar límites
        if (newX < 0 || newX >= gridSize || newY < 0 || newY >= gridSize) {
            return false
        }
        
        // Verificar pared
        if (maze[newY][newX] == 1) {
            return false
        }
        
        // Mover jugador
        playerPosition = GridPosition(newX, newY)
        path.add(playerPosition)
        moves++
        
        onPositionChanged(playerPosition)
        
        // Verificar si llegó a la meta
        if (playerPosition.x == goalPosition.x && playerPosition.y == goalPosition.y) {
            gameWon = true
            score = calculateScore()
            onGameWon(score, moves)
        }
        
        return true
    }
    
    /**
     * Calcular puntuación basada en movimientos
     */
    private fun calculateScore(): Int {
        val optimalMoves = (gridSize - 1) * 2 // Mínimo de movimientos posibles
        val efficiency = optimalMoves.toFloat() / moves.toFloat()
        return (efficiency * 1000).toInt().coerceAtLeast(100)
    }
    
    /**
     * Obtener el tipo de celda en una posición
     */
    fun getCellType(x: Int, y: Int): CellType {
        return when {
            x == playerPosition.x && y == playerPosition.y -> CellType.PLAYER
            x == goalPosition.x && y == goalPosition.y -> CellType.GOAL
            maze[y][x] == 1 -> CellType.WALL
            path.contains(GridPosition(x, y)) -> CellType.PATH
            else -> CellType.EMPTY
        }
    }
    
    /**
     * Obtener la posición del jugador
     */
    fun getPlayerPosition(): GridPosition = playerPosition
    
    /**
     * Obtener la posición de la meta
     */
    fun getGoalPosition(): GridPosition = goalPosition
    
    /**
     * Obtener el laberinto completo
     */
    fun getMaze(): Array<IntArray> = maze
    
    /**
     * Obtener el camino recorrido
     */
    fun getPath(): List<GridPosition> = path.toList()
    
    /**
     * Iniciar el juego
     */
    fun start() {
        gameStarted = true
    }
    
    /**
     * Reiniciar el juego
     */
    fun restart() {
        playerPosition = GridPosition(0, 0)
        path.clear()
        path.add(playerPosition)
        moves = 0
        score = 0
        gameWon = false
        gameStarted = false
        generateMaze()
    }
    
    /**
     * Obtener estado del juego
     */
    fun getGameState(): MazeGameState {
        return MazeGameState(
            playerPosition = playerPosition,
            goalPosition = goalPosition,
            score = score,
            moves = moves,
            gameWon = gameWon,
            gameStarted = gameStarted
        )
    }
}
