package com.example.eyegestures

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel para el juego de Laberinto
 * Conecta pupil tracking calibrado → MazeGame → UI (Compose)
 * 
 * Responsabilidades:
 * 1. Mantener instancia de MazeGame
 * 2. Exponer estado observable para Compose
 * 3. Recibir posición de pupila y convertir a movimientos
 * 4. Reaccionar a parpadeos (más simple que Snake, no necesita game loop)
 */
class MazeViewModel : ViewModel() {
    
    // ========================================
    // INSTANCIA DEL JUEGO
    // ========================================
    
    private lateinit var mazeGame: MazeGame
    
    // Controlador de pupil tracking
    private var pupilController: PupilTrackingController? = null
    
    // ========================================
    // ESTADO OBSERVABLE (StateFlow)
    // ========================================
    
    // Estado principal del juego
    private val _gameState = MutableStateFlow(
        MazeGameUiState(
            playerPosition = GridPosition(0, 0),
            goalPosition = GridPosition(9, 9),
            maze = Array(10) { IntArray(10) { 0 } },
            path = emptyList(),
            moves = 0,
            score = 0,
            gameWon = false,
            gameStarted = false
        )
    )
    val gameState: StateFlow<MazeGameUiState> = _gameState.asStateFlow()
    
    // Control de debounce para movimientos
    private var lastMoveTime = 0L
    private val MOVE_DEBOUNCE_MS = 300L
    
    // ========================================
    // INICIALIZACIÓN
    // ========================================
    
    init {
        initializeGame(10)
    }
    
    fun initializeGame(gridSize: Int) {
        mazeGame = MazeGame(
            gridSize = gridSize,
            onPositionChanged = { _ ->
                updateGameState()
            },
            onGameWon = { _, _ ->
                updateGameState()
            }
        )
        
        // Inicializar controlador de pupil tracking
        // Usamos un tamaño de pantalla estimado (se puede pasar como parámetro)
        val calibrationManager = CalibrationViewModel.getSharedCalibrationManager()
        pupilController = PupilTrackingController(
            screenWidth = 1080, // TODO: Obtener tamaño real de pantalla
            screenHeight = 1920,
            calibrationManager = calibrationManager
        ).apply {
            setDeadZone(0.25f) // Zona muerta más pequeña para laberinto (más sensible)
        }
        
        // Observar cambios de dirección del pupil tracking
        viewModelScope.launch {
            pupilController?.currentDirection?.collect { direction ->
                when (direction) {
                    GameDirection.UP -> movePlayer(Direction.UP)
                    GameDirection.DOWN -> movePlayer(Direction.DOWN)
                    GameDirection.LEFT -> movePlayer(Direction.LEFT)
                    GameDirection.RIGHT -> movePlayer(Direction.RIGHT)
                    GameDirection.NONE -> { /* Sin movimiento */ }
                }
            }
        }
        
        updateGameState()
    }
    
    /**
     * Actualiza la posición de la pupila detectada por OpenCV
     * 
     * @param pupilX Coordenada X de la pupila
     * @param pupilY Coordenada Y de la pupila
     */
    fun updatePupilPosition(pupilX: Float, pupilY: Float) {
        pupilController?.updatePupilPosition(pupilX, pupilY)
        
        // También actualizar el cursor visual global
        val screenPos = pupilController?.screenPosition?.value
        if (screenPos != null) {
            GazeCursorManager.updateGazePosition(screenPos.x, screenPos.y)
        }
    }
    
    // ========================================
    // CONTROL DEL MOVIMIENTO
    // ========================================
    
    /**
     * Mover jugador (desde UI o sistema de pupil tracking)
     */
    fun movePlayer(direction: Direction): Boolean {
        if (!gameState.value.gameStarted || gameState.value.gameWon) return false
        
        val moved = mazeGame.movePlayer(direction)
        
        if (moved) {
            updateGameState()
        }
        
        return moved
    }
    
    /**
     * Detectar parpadeo (para iniciar o reiniciar)
     */
    fun onBlinkDetected() {
        val currentState = gameState.value
        
        when {
            // Si ganó, reiniciar
            currentState.gameWon -> restart()
            
            // Si no ha comenzado, iniciar
            !currentState.gameStarted -> start()
            
            // Si está jugando, puede dar una pista (opcional)
            else -> {
                // Aquí podrías implementar una función de pista
                // Por ejemplo, iluminar el siguiente paso correcto
            }
        }
    }
    
    // ========================================
    // CONTROL DEL JUEGO
    // ========================================
    
    /**
     * Iniciar el juego
     * No necesita game loop, solo reacciona a movimientos
     */
    fun start() {
        mazeGame.start()
        updateGameState()
    }
    
    /**
     * Reiniciar el juego con nuevo laberinto
     */
    fun restart() {
        mazeGame.restart()
        lastMoveTime = 0L
        updateGameState()
    }
    
    /**
     * Obtener el tipo de celda en una posición
     * Útil para dibujar el laberinto
     */
    fun getCellType(x: Int, y: Int): CellType {
        return mazeGame.getCellType(x, y)
    }
    
    // ========================================
    // ACTUALIZACIÓN DE ESTADO
    // ========================================
    
    /**
     * Actualizar el estado observable desde MazeGame
     * Esto dispara la recomposición en Compose
     */
    private fun updateGameState() {
        val currentGameState = mazeGame.getGameState()
        
        _gameState.value = MazeGameUiState(
            playerPosition = currentGameState.playerPosition,
            goalPosition = currentGameState.goalPosition,
            maze = mazeGame.getMaze(),
            path = mazeGame.getPath(),
            moves = mazeGame.moves,
            score = mazeGame.score,
            gameWon = mazeGame.gameWon,
            gameStarted = mazeGame.gameStarted
        )
    }
    
    // ========================================
    // CLEANUP
    // ========================================
    
    override fun onCleared() {
        super.onCleared()
        // No hay game loop que detener
    }
}

/**
 * Estado de la UI del juego de Laberinto
 * Se expone a través de StateFlow para que Compose observe cambios
 */
data class MazeGameUiState(
    val playerPosition: GridPosition,
    val goalPosition: GridPosition,
    val maze: Array<IntArray>,
    val path: List<GridPosition>,
    val moves: Int,
    val score: Int,
    val gameWon: Boolean,
    val gameStarted: Boolean
) {
    // Override equals y hashCode para arrays
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false

        other as MazeGameUiState

        if (playerPosition != other.playerPosition) return false
        if (goalPosition != other.goalPosition) return false
        if (!maze.contentDeepEquals(other.maze)) return false
        if (path != other.path) return false
        if (moves != other.moves) return false
        if (score != other.score) return false
        if (gameWon != other.gameWon) return false
        if (gameStarted != other.gameStarted) return false

        return true
    }

    override fun hashCode(): Int {
        var result = playerPosition.hashCode()
        result = 31 * result + goalPosition.hashCode()
        result = 31 * result + maze.contentDeepHashCode()
        result = 31 * result + path.hashCode()
        result = 31 * result + moves
        result = 31 * result + score
        result = 31 * result + gameWon.hashCode()
        result = 31 * result + gameStarted.hashCode()
        return result
    }
}
