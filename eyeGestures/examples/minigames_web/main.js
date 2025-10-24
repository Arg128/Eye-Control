// Main Application Logic
let currentGame = null;

function loadGame(gameName) {
    const GameClass = games[gameName];
    
    if (!GameClass) {
        alert('Este juego aún no está disponible. ¡Próximamente!');
        return;
    }
    
    // Hide main menu
    document.getElementById('mainMenu').classList.add('hidden');
    
    // Show game container
    const gameContainer = document.getElementById('gameContainer');
    gameContainer.classList.remove('hidden');
    
    // Set game title
    const canvas = document.getElementById('gameCanvas');
    currentGame = new GameClass(canvas);
    document.getElementById('currentGameTitle').textContent = currentGame.title;
    
    // Start the game
    currentGame.start();
}

function backToMenu() {
    // Stop current game
    if (currentGame) {
        currentGame.stop();
        currentGame = null;
    }
    
    // Hide game container
    document.getElementById('gameContainer').classList.add('hidden');
    
    // Show main menu
    document.getElementById('mainMenu').classList.remove('hidden');
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && currentGame) {
        backToMenu();
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('EyeGestures Minigames loaded successfully!');
    console.log('Eye tracking status:', eyeTracking.fallbackMode ? 'Mouse mode' : 'Connected');
    
    // Escuchar eventos del sistema de eye tracking
    eyeTracking.addListener((data) => {
        // Actualizar indicador de calibración
        if (eyeTracking.calibrating) {
            const indicator = document.getElementById('calibrationIndicator');
            const progress = document.getElementById('calibrationProgress');
            const text = document.getElementById('calibrationText');
            
            if (indicator) {
                indicator.style.display = 'flex';
                const percentage = (eyeTracking.calibrationProgress / 60) * 100;
                progress.style.width = `${percentage}%`;
                text.textContent = `Calibrando... ${Math.round(percentage)}%`;
            }
        } else {
            // Ocultar cuando termine la calibración
            const indicator = document.getElementById('calibrationIndicator');
            if (indicator && indicator.style.display !== 'none' && eyeTracking.calibrationProgress >= 60) {
                setTimeout(() => {
                    indicator.style.display = 'none';
                }, 2000);
            }
        }
    });
});
