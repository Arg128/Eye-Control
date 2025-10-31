package com.example.eyegestures

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel para el juego Snake
 * Conecta pupil tracking calibrado → SnakeGame → UI (Compose)
 * 
 * Responsabilidades:
 * 1. Mantener instancia de SnakeGame
 * 2. Exponer estado observable para Compose
 * 3. Game loop con viewModelScope (5 veces por segundo)
 * 4. Recibir posición de pupila y convertir a direcciones de juego
 */
class SnakeViewModel : ViewModel() {
    
    // ========================================
    // INSTANCIA DEL JUEGO
    // ========================================
    
    private lateinit var snakeGame: SnakeGame
    
    // Controlador de pupil tracking (se inicializa después)
    private var pupilController: PupilTrackingController? = null
    
    // ========================================
    // ESTADO OBSERVABLE (StateFlow)
    // ========================================
    
    // Estado principal del juego
    private val _gameState = MutableStateFlow(
        SnakeGameUiState(
            score = 0,
            snake = emptyList(),
            food = GridPosition(0, 0),
            direction = Direction.RIGHT,
            gameOver = false,
            gameStarted = false,
            isPaused = false
        )
    )
    val gameState: StateFlow<SnakeGameUiState> = _gameState.asStateFlow()
    
    // Job del game loop
    private var gameLoopJob: Job? = null
    
    // ========================================
    // INICIALIZACIÓN
    // ========================================
    
    init {
        initializeGame(800f, 800f)
    }
    
    fun initializeGame(canvasWidth: Float, canvasHeight: Float) {
        snakeGame = SnakeGame(
            canvasWidth = canvasWidth,
            canvasHeight = canvasHeight,
            onScoreChanged = { _ ->
                updateGameState()
            },
            onGameOver = { _ ->
                updateGameState()
                stopGameLoop()
            }
        )
        
        // Inicializar controlador de pupil tracking
        val calibrationManager = CalibrationViewModel.getSharedCalibrationManager()
        pupilController = PupilTrackingController(
            screenWidth = canvasWidth.toInt(),
            screenHeight = canvasHeight.toInt(),
            calibrationManager = calibrationManager
        )
        
        // Observar cambios de dirección del pupil tracking
        viewModelScope.launch {
            pupilController?.currentDirection?.collect { direction ->
                if (direction != GameDirection.NONE) {
                    changeDirection(direction)
                }
            }
        }
        
        updateGameState()
    }
    
    // ========================================
    // CONTROL DE DIRECCIÓN Y PARPADEO
    // ========================================
    
    /**
     * Actualiza la posición de la pupila detectada por OpenCV
     * 
     * Llama esta función continuamente desde tu detector de pupila
     * 
     * @param pupilX Coordenada X de la pupila
     * @param pupilY Coordenada Y de la pupila
     */
    fun updatePupilPosition(pupilX: Float, pupilY: Float) {
        pupilController?.updatePupilPosition(pupilX, pupilY)
        
        // También actualizar el cursor visual global
        // El PupilTrackingController ya hace el mapeo a coordenadas de pantalla
        val screenPos = pupilController?.screenPosition?.value
        if (screenPos != null) {
            GazeCursorManager.updateGazePosition(screenPos.x, screenPos.y)
        }
    }
    
    /**
     * Cambiar dirección del Snake (desde UI, pupil tracking o controles táctiles)
     */
    fun changeDirection(direction: GameDirection) {
        if (!gameState.value.gameStarted || gameState.value.gameOver) return
        
        snakeGame.updateDirectionFromGaze(direction)
        updateGameState()
    }
    
    /**
     * Detectar parpadeo (para pausar/reanudar o reiniciar)
     */
    fun onBlinkDetected() {
        val currentState = gameState.value
        
        when {
            // Si game over, reiniciar
            currentState.gameOver -> restart()
            
            // Si no ha comenzado, iniciar
            !currentState.gameStarted -> start()
            
            // Si está jugando, pausar/reanudar
            else -> togglePause()
        }
    }
    
    // ========================================
    // GAME LOOP (5 veces por segundo)
    // ========================================
    // ========================================
    // GAME LOOP (5 veces por segundo)
    // ========================================
    
    /**
     * Iniciar el game loop
     * Se ejecuta 5 veces por segundo (cada 200ms)
     */
    private fun startGameLoop() {
        gameLoopJob?.cancel()
        
        gameLoopJob = viewModelScope.launch {
            while (true) {
                if (!gameState.value.isPaused && !gameState.value.gameOver) {
                    // Actualizar el juego
                    val updated = snakeGame.updateGame()
                    
                    if (updated) {
                        // Actualizar estado observable
                        updateGameState()
                    }
                }
                
                // Delay para 5 actualizaciones por segundo
                delay(200) // 200ms = 1000ms / 5
            }
        }
    }
    
    /**
     * Detener el game loop
     */
    private fun stopGameLoop() {
        gameLoopJob?.cancel()
        gameLoopJob = null
    }
    
    // ========================================
    // CONTROL DEL JUEGO
    // ========================================
    
    /**
     * Iniciar el juego
     */
    fun start() {
        snakeGame.start()
        updateGameState()
        startGameLoop()
    }
    
    /**
     * Pausar/Reanudar el juego
     */
    fun togglePause() {
        val newPauseState = !gameState.value.isPaused
        _gameState.value = _gameState.value.copy(isPaused = newPauseState)
    }
    
    /**
     * Reiniciar el juego
     */
    fun restart() {
        stopGameLoop()
        snakeGame.restart()
        updateGameState()
        start()
    }
    
    /**
     * Detener el juego
     */
    fun stop() {
        snakeGame.stop()
        stopGameLoop()
        updateGameState()
    }
    
    // ========================================
    // ACTUALIZACIÓN DE ESTADO
    // ========================================
    
    /**
     * Actualizar el estado observable desde SnakeGame
     * Esto dispara la recomposición en Compose
     */
    private fun updateGameState() {
        val currentGameState = snakeGame.getGameState()
        
        _gameState.value = SnakeGameUiState(
            score = currentGameState.score,
            snake = snakeGame.getSnake(),
            food = snakeGame.getFood(),
            direction = snakeGame.getCurrentDirection(),
            gameOver = currentGameState.gameOver,
            gameStarted = currentGameState.running,
            isPaused = gameState.value.isPaused
        )
    }
    
    // ========================================
    // CLEANUP
    // ========================================
    
    override fun onCleared() {
        super.onCleared()
        stopGameLoop()
        snakeGame.destroy()
    }
}

/**
 * Estado de la UI del juego Snake
 * Se expone a través de StateFlow para que Compose observe cambios
 */
data class SnakeGameUiState(
    val score: Int,
    val snake: List<GridPosition>,
    val food: GridPosition,
    val direction: Direction,
    val gameOver: Boolean,
    val gameStarted: Boolean,
    val isPaused: Boolean
)
