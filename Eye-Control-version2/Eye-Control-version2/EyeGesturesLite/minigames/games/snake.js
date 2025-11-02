/**
 * Eye Snake - Juego de serpiente controlado con la mirada
 */

class EyeSnake {
    constructor(canvas, gazeCallback) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.gazeCallback = gazeCallback;
        
        // Configurar canvas
        this.canvas.width = window.innerWidth * 0.9;
        this.canvas.height = window.innerHeight * 0.7;
        
        this.score = 0;
        this.gameOver = false;
        this.running = false;
        
        this.gridSize = 20;
        this.cols = Math.floor(this.canvas.width / this.gridSize);
        this.rows = Math.floor(this.canvas.height / this.gridSize);
        
        // Cursor de mirada para dirección
        this.gaze = {
            x: this.canvas.width / 2,
            y: this.canvas.height / 2
        };
        
        // Serpiente
        this.snake = [];
        this.direction = { x: 1, y: 0 };
        this.nextDirection = { x: 1, y: 0 };
        
        // Comida
        this.food = { x: 0, y: 0 };
        
        // Tiempo
        this.lastMove = Date.now();
        this.moveInterval = 150; // ms entre movimientos
        
        this.init();
    }
    
    init() {
        // Inicializar serpiente en el centro
        const centerX = Math.floor(this.cols / 2);
        const centerY = Math.floor(this.rows / 2);
        
        this.snake = [
            { x: centerX, y: centerY },
            { x: centerX - 1, y: centerY },
            { x: centerX - 2, y: centerY }
        ];
        
        this.spawnFood();
    }
    
    spawnFood() {
        let validPosition = false;
        
        while (!validPosition) {
            this.food.x = Math.floor(Math.random() * this.cols);
            this.food.y = Math.floor(Math.random() * this.rows);
            
            // Verificar que no esté en la serpiente
            validPosition = !this.snake.some(segment => 
                segment.x === this.food.x && segment.y === this.food.y
            );
        }
    }
    
    onGaze(x, y) {
        const canvasRect = this.canvas.getBoundingClientRect();
        this.gaze.x = x - canvasRect.left;
        this.gaze.y = y - canvasRect.top;
        
        // Calcular dirección basada en la posición de la mirada
        const head = this.snake[0];
        const headPixelX = head.x * this.gridSize + this.gridSize / 2;
        const headPixelY = head.y * this.gridSize + this.gridSize / 2;
        
        const dx = this.gaze.x - headPixelX;
        const dy = this.gaze.y - headPixelY;
        
        // Determinar dirección predominante
        if (Math.abs(dx) > Math.abs(dy)) {
            // Movimiento horizontal
            if (dx > 0 && this.direction.x !== -1) {
                this.nextDirection = { x: 1, y: 0 };
            } else if (dx < 0 && this.direction.x !== 1) {
                this.nextDirection = { x: -1, y: 0 };
            }
        } else {
            // Movimiento vertical
            if (dy > 0 && this.direction.y !== -1) {
                this.nextDirection = { x: 0, y: 1 };
            } else if (dy < 0 && this.direction.y !== 1) {
                this.nextDirection = { x: 0, y: -1 };
            }
        }
    }
    
    update() {
        if (this.gameOver) return;
        
        const now = Date.now();
        if (now - this.lastMove < this.moveInterval) return;
        
        this.lastMove = now;
        
        // Actualizar dirección
        this.direction = { ...this.nextDirection };
        
        // Calcular nueva posición de la cabeza
        const head = this.snake[0];
        const newHead = {
            x: head.x + this.direction.x,
            y: head.y + this.direction.y
        };
        
        // Verificar colisión con bordes (wrap around)
        if (newHead.x < 0) newHead.x = this.cols - 1;
        if (newHead.x >= this.cols) newHead.x = 0;
        if (newHead.y < 0) newHead.y = this.rows - 1;
        if (newHead.y >= this.rows) newHead.y = 0;
        
        // Verificar colisión con sí misma
        if (this.snake.some(segment => segment.x === newHead.x && segment.y === newHead.y)) {
            this.gameOver = true;
            this.showGameOver();
            return;
        }
        
        // Añadir nueva cabeza
        this.snake.unshift(newHead);
        
        // Verificar si comió
        if (newHead.x === this.food.x && newHead.y === this.food.y) {
            this.score += 10;
            this.updateScore();
            this.spawnFood();
            
            // Aumentar velocidad ligeramente
            this.moveInterval = Math.max(50, this.moveInterval - 2);
        } else {
            // Quitar cola si no comió
            this.snake.pop();
        }
    }
    
    draw() {
        // Limpiar canvas
        this.ctx.fillStyle = '#1a1a2e';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Dibujar grid sutil
        this.ctx.strokeStyle = '#16213e';
        this.ctx.lineWidth = 1;
        for (let i = 0; i < this.cols; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(i * this.gridSize, 0);
            this.ctx.lineTo(i * this.gridSize, this.canvas.height);
            this.ctx.stroke();
        }
        for (let i = 0; i < this.rows; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, i * this.gridSize);
            this.ctx.lineTo(this.canvas.width, i * this.gridSize);
            this.ctx.stroke();
        }
        
        // Dibujar comida
        const foodX = this.food.x * this.gridSize;
        const foodY = this.food.y * this.gridSize;
        
        // Efecto pulsante para la comida
        const pulse = Math.sin(Date.now() / 200) * 2 + 2;
        this.ctx.fillStyle = '#ff5757';
        this.ctx.beginPath();
        this.ctx.arc(
            foodX + this.gridSize / 2,
            foodY + this.gridSize / 2,
            this.gridSize / 2 - 2 + pulse,
            0,
            Math.PI * 2
        );
        this.ctx.fill();
        
        // Dibujar serpiente
        this.snake.forEach((segment, index) => {
            const x = segment.x * this.gridSize;
            const y = segment.y * this.gridSize;
            
            if (index === 0) {
                // Cabeza
                this.ctx.fillStyle = '#4CAF50';
                this.ctx.fillRect(x + 1, y + 1, this.gridSize - 2, this.gridSize - 2);
                
                // Ojos
                this.ctx.fillStyle = '#FFF';
                const eyeSize = 3;
                const eyeOffset = 5;
                
                if (this.direction.x === 1) {
                    // Derecha
                    this.ctx.fillRect(x + this.gridSize - eyeOffset, y + eyeOffset, eyeSize, eyeSize);
                    this.ctx.fillRect(x + this.gridSize - eyeOffset, y + this.gridSize - eyeOffset - eyeSize, eyeSize, eyeSize);
                } else if (this.direction.x === -1) {
                    // Izquierda
                    this.ctx.fillRect(x + eyeOffset - eyeSize, y + eyeOffset, eyeSize, eyeSize);
                    this.ctx.fillRect(x + eyeOffset - eyeSize, y + this.gridSize - eyeOffset - eyeSize, eyeSize, eyeSize);
                } else if (this.direction.y === 1) {
                    // Abajo
                    this.ctx.fillRect(x + eyeOffset, y + this.gridSize - eyeOffset, eyeSize, eyeSize);
                    this.ctx.fillRect(x + this.gridSize - eyeOffset - eyeSize, y + this.gridSize - eyeOffset, eyeSize, eyeSize);
                } else {
                    // Arriba
                    this.ctx.fillRect(x + eyeOffset, y + eyeOffset - eyeSize, eyeSize, eyeSize);
                    this.ctx.fillRect(x + this.gridSize - eyeOffset - eyeSize, y + eyeOffset - eyeSize, eyeSize, eyeSize);
                }
            } else {
                // Cuerpo con gradiente
                const alpha = 1 - (index / this.snake.length) * 0.5;
                this.ctx.fillStyle = `rgba(76, 175, 80, ${alpha})`;
                this.ctx.fillRect(x + 2, y + 2, this.gridSize - 4, this.gridSize - 4);
            }
        });
        
        // Dibujar indicador de mirada
        this.ctx.strokeStyle = 'rgba(255, 215, 0, 0.5)';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(this.gaze.x, this.gaze.y, 15, 0, Math.PI * 2);
        this.ctx.stroke();
        
        // Línea de la cabeza a la mirada
        const head = this.snake[0];
        const headPixelX = head.x * this.gridSize + this.gridSize / 2;
        const headPixelY = head.y * this.gridSize + this.gridSize / 2;
        
        this.ctx.strokeStyle = 'rgba(255, 215, 0, 0.3)';
        this.ctx.lineWidth = 1;
        this.ctx.setLineDash([5, 5]);
        this.ctx.beginPath();
        this.ctx.moveTo(headPixelX, headPixelY);
        this.ctx.lineTo(this.gaze.x, this.gaze.y);
        this.ctx.stroke();
        this.ctx.setLineDash([]);
        
        // Instrucciones
        if (!this.running) {
            this.ctx.fillStyle = '#FFF';
            this.ctx.font = '24px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('Mira en la dirección que quieres que vaya la serpiente', this.canvas.width / 2, 50);
        }
        
        // Game Over
        if (this.gameOver) {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            
            this.ctx.fillStyle = '#ff5757';
            this.ctx.font = 'bold 48px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('GAME OVER', this.canvas.width / 2, this.canvas.height / 2 - 20);
            
            this.ctx.fillStyle = '#FFF';
            this.ctx.font = '24px Arial';
            this.ctx.fillText(`Puntuación Final: ${this.score}`, this.canvas.width / 2, this.canvas.height / 2 + 30);
        }
    }
    
    showGameOver() {
        setTimeout(() => {
            const gameInfo = document.getElementById('game-info');
            if (gameInfo) {
                gameInfo.innerHTML = `
                    <div style="color: #ff5757; font-size: 24px; margin-top: 20px;">
                        ¡Te chocaste! Puntuación: ${this.score}
                    </div>
                `;
            }
        }, 100);
    }
    
    updateScore() {
        const scoreEl = document.getElementById('score');
        if (scoreEl) {
            scoreEl.textContent = this.score;
        }
    }
    
    start() {
        this.running = true;
        this.gameLoop();
    }
    
    gameLoop() {
        if (!this.running) return;
        
        this.update();
        this.draw();
        
        requestAnimationFrame(() => this.gameLoop());
    }
    
    stop() {
        this.running = false;
    }
    
    destroy() {
        this.stop();
    }
}

window.EyeSnake = EyeSnake;
