/**
 * Eye Pong - Juego de Pong controlado con la mirada
 */

class EyePong {
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
        
        // Paleta del jugador (controlada por ojos)
        this.paddle = {
            x: 50,
            y: this.canvas.height / 2,
            width: 15,
            height: 100,
            speed: 8,
            targetY: this.canvas.height / 2
        };
        
        // Paleta de la IA
        this.aiPaddle = {
            x: this.canvas.width - 65,
            y: this.canvas.height / 2,
            width: 15,
            height: 100,
            speed: 5
        };
        
        // Pelota
        this.ball = {
            x: this.canvas.width / 2,
            y: this.canvas.height / 2,
            radius: 10,
            speedX: 6,
            speedY: 6,
            maxSpeed: 12
        };
        
        // Partículas para efectos
        this.particles = [];
        
        this.init();
    }
    
    init() {
        this.resetBall();
    }
    
    resetBall() {
        this.ball.x = this.canvas.width / 2;
        this.ball.y = this.canvas.height / 2;
        this.ball.speedX = (Math.random() > 0.5 ? 1 : -1) * 6;
        this.ball.speedY = (Math.random() - 0.5) * 8;
    }
    
    onGaze(x, y) {
        // Mapear la posición Y de la mirada a la posición de la paleta
        const canvasRect = this.canvas.getBoundingClientRect();
        const relativeY = y - canvasRect.top;
        
        // Suavizar el movimiento
        this.paddle.targetY = Math.max(
            this.paddle.height / 2,
            Math.min(this.canvas.height - this.paddle.height / 2, relativeY)
        );
    }
    
    update() {
        if (this.gameOver) return;
        
        // Mover paleta del jugador suavemente hacia el objetivo
        const diff = this.paddle.targetY - this.paddle.y;
        this.paddle.y += diff * 0.2; // Suavizado
        
        // IA sigue la pelota
        const aiTarget = this.ball.y;
        if (this.aiPaddle.y + this.aiPaddle.height / 2 < aiTarget - 10) {
            this.aiPaddle.y += this.aiPaddle.speed;
        } else if (this.aiPaddle.y + this.aiPaddle.height / 2 > aiTarget + 10) {
            this.aiPaddle.y -= this.aiPaddle.speed;
        }
        
        // Mantener IA en límites
        this.aiPaddle.y = Math.max(0, Math.min(this.canvas.height - this.aiPaddle.height, this.aiPaddle.y));
        
        // Mover pelota
        this.ball.x += this.ball.speedX;
        this.ball.y += this.ball.speedY;
        
        // Colisión con bordes superior e inferior
        if (this.ball.y - this.ball.radius < 0 || this.ball.y + this.ball.radius > this.canvas.height) {
            this.ball.speedY *= -1;
            this.createParticles(this.ball.x, this.ball.y, '#FFF');
        }
        
        // Colisión con paleta del jugador
        if (this.ball.x - this.ball.radius < this.paddle.x + this.paddle.width &&
            this.ball.x + this.ball.radius > this.paddle.x &&
            this.ball.y > this.paddle.y &&
            this.ball.y < this.paddle.y + this.paddle.height) {
            
            this.ball.speedX = Math.abs(this.ball.speedX);
            // Añadir efecto según dónde golpea
            const hitPos = (this.ball.y - this.paddle.y) / this.paddle.height;
            this.ball.speedY = (hitPos - 0.5) * 10;
            
            // Incrementar velocidad ligeramente
            this.ball.speedX = Math.min(this.ball.speedX * 1.05, this.ball.maxSpeed);
            
            this.score += 10;
            this.createParticles(this.ball.x, this.ball.y, '#4CAF50');
            this.updateScore();
        }
        
        // Colisión con paleta IA
        if (this.ball.x + this.ball.radius > this.aiPaddle.x &&
            this.ball.x - this.ball.radius < this.aiPaddle.x + this.aiPaddle.width &&
            this.ball.y > this.aiPaddle.y &&
            this.ball.y < this.aiPaddle.y + this.aiPaddle.height) {
            
            this.ball.speedX = -Math.abs(this.ball.speedX);
            const hitPos = (this.ball.y - this.aiPaddle.y) / this.aiPaddle.height;
            this.ball.speedY = (hitPos - 0.5) * 10;
            
            this.createParticles(this.ball.x, this.ball.y, '#ff5757');
        }
        
        // Pelota sale por la izquierda (punto para IA)
        if (this.ball.x - this.ball.radius < 0) {
            this.resetBall();
            if (this.score > 0) this.score -= 5;
            this.updateScore();
        }
        
        // Pelota sale por la derecha (punto para jugador)
        if (this.ball.x + this.ball.radius > this.canvas.width) {
            this.resetBall();
            this.score += 50;
            this.updateScore();
            this.createParticles(this.canvas.width / 2, this.canvas.height / 2, '#FFD700');
        }
        
        // Actualizar partículas
        this.particles = this.particles.filter(p => p.life > 0);
        this.particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.life--;
        });
    }
    
    createParticles(x, y, color) {
        for (let i = 0; i < 10; i++) {
            this.particles.push({
                x: x,
                y: y,
                vx: (Math.random() - 0.5) * 4,
                vy: (Math.random() - 0.5) * 4,
                life: 30,
                color: color
            });
        }
    }
    
    draw() {
        // Limpiar canvas
        this.ctx.fillStyle = '#1a1a2e';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Línea central
        this.ctx.strokeStyle = '#16213e';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([10, 10]);
        this.ctx.beginPath();
        this.ctx.moveTo(this.canvas.width / 2, 0);
        this.ctx.lineTo(this.canvas.width / 2, this.canvas.height);
        this.ctx.stroke();
        this.ctx.setLineDash([]);
        
        // Paleta del jugador
        this.ctx.fillStyle = '#4CAF50';
        this.ctx.fillRect(this.paddle.x, this.paddle.y, this.paddle.width, this.paddle.height);
        
        // Paleta IA
        this.ctx.fillStyle = '#ff5757';
        this.ctx.fillRect(this.aiPaddle.x, this.aiPaddle.y, this.aiPaddle.width, this.aiPaddle.height);
        
        // Pelota
        this.ctx.fillStyle = '#FFF';
        this.ctx.beginPath();
        this.ctx.arc(this.ball.x, this.ball.y, this.ball.radius, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Partículas
        this.particles.forEach(p => {
            this.ctx.fillStyle = p.color;
            this.ctx.globalAlpha = p.life / 30;
            this.ctx.fillRect(p.x, p.y, 3, 3);
        });
        this.ctx.globalAlpha = 1;
        
        // Instrucciones
        if (!this.running) {
            this.ctx.fillStyle = '#FFF';
            this.ctx.font = '24px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('Mueve tu mirada arriba y abajo para controlar la paleta verde', this.canvas.width / 2, 50);
        }
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

window.EyePong = EyePong;
