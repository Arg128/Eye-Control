/**
 * Eye Collect - Juego de recolectar estrellas con la mirada
 */

class EyeCollect {
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
        this.timeLeft = 60; // 60 segundos
        
        // Jugador (cursor de mirada)
        this.player = {
            x: this.canvas.width / 2,
            y: this.canvas.height / 2,
            radius: 25,
            targetX: this.canvas.width / 2,
            targetY: this.canvas.height / 2
        };
        
        // Estrellas
        this.stars = [];
        this.maxStars = 8;
        
        // Obstáculos (evitar tocarlos)
        this.obstacles = [];
        this.maxObstacles = 5;
        
        // Efectos
        this.particles = [];
        
        // Timer
        this.gameStartTime = Date.now();
        
        this.init();
    }
    
    init() {
        // Generar estrellas iniciales
        for (let i = 0; i < this.maxStars; i++) {
            this.spawnStar();
        }
        
        // Generar obstáculos
        for (let i = 0; i < this.maxObstacles; i++) {
            this.spawnObstacle();
        }
    }
    
    spawnStar() {
        const margin = 60;
        const star = {
            x: margin + Math.random() * (this.canvas.width - margin * 2),
            y: margin + Math.random() * (this.canvas.height - margin * 2),
            radius: 15 + Math.random() * 10,
            points: Math.floor(5 + Math.random() * 15),
            rotation: 0,
            rotationSpeed: 0.05 + Math.random() * 0.1,
            pulsePhase: Math.random() * Math.PI * 2
        };
        
        this.stars.push(star);
    }
    
    spawnObstacle() {
        const margin = 80;
        const obstacle = {
            x: margin + Math.random() * (this.canvas.width - margin * 2),
            y: margin + Math.random() * (this.canvas.height - margin * 2),
            radius: 20 + Math.random() * 15,
            speedX: (Math.random() - 0.5) * 2,
            speedY: (Math.random() - 0.5) * 2,
            rotation: 0,
            rotationSpeed: 0.02
        };
        
        this.obstacles.push(obstacle);
    }
    
    onGaze(x, y) {
        const canvasRect = this.canvas.getBoundingClientRect();
        this.player.targetX = x - canvasRect.left;
        this.player.targetY = y - canvasRect.top;
    }
    
    update() {
        if (this.gameOver) return;
        
        // Actualizar timer
        const elapsed = (Date.now() - this.gameStartTime) / 1000;
        this.timeLeft = Math.max(0, 60 - elapsed);
        
        if (this.timeLeft <= 0) {
            this.gameOver = true;
            this.showGameOver();
            return;
        }
        
        // Mover jugador suavemente hacia la mirada
        const dx = this.player.targetX - this.player.x;
        const dy = this.player.targetY - this.player.y;
        
        this.player.x += dx * 0.15;
        this.player.y += dy * 0.15;
        
        // Mantener dentro del canvas
        this.player.x = Math.max(this.player.radius, Math.min(this.canvas.width - this.player.radius, this.player.x));
        this.player.y = Math.max(this.player.radius, Math.min(this.canvas.height - this.player.radius, this.player.y));
        
        // Actualizar estrellas
        this.stars.forEach((star, index) => {
            star.rotation += star.rotationSpeed;
            
            // Verificar colisión con jugador
            const dist = Math.hypot(this.player.x - star.x, this.player.y - star.y);
            if (dist < this.player.radius + star.radius) {
                this.score += star.points;
                this.updateScore();
                this.createParticles(star.x, star.y, '#FFD700');
                this.stars.splice(index, 1);
                this.spawnStar();
            }
        });
        
        // Actualizar obstáculos
        this.obstacles.forEach(obstacle => {
            obstacle.x += obstacle.speedX;
            obstacle.y += obstacle.speedY;
            obstacle.rotation += obstacle.rotationSpeed;
            
            // Rebotar en bordes
            if (obstacle.x - obstacle.radius < 0 || obstacle.x + obstacle.radius > this.canvas.width) {
                obstacle.speedX *= -1;
            }
            if (obstacle.y - obstacle.radius < 0 || obstacle.y + obstacle.radius > this.canvas.height) {
                obstacle.speedY *= -1;
            }
            
            // Verificar colisión con jugador
            const dist = Math.hypot(this.player.x - obstacle.x, this.player.y - obstacle.y);
            if (dist < this.player.radius + obstacle.radius) {
                this.score = Math.max(0, this.score - 10);
                this.updateScore();
                this.createParticles(obstacle.x, obstacle.y, '#ff5757');
                
                // Empujar obstáculo
                const angle = Math.atan2(obstacle.y - this.player.y, obstacle.x - this.player.x);
                obstacle.speedX = Math.cos(angle) * 3;
                obstacle.speedY = Math.sin(angle) * 3;
            }
        });
        
        // Actualizar partículas
        this.particles = this.particles.filter(p => p.life > 0);
        this.particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.1; // Gravedad leve
            p.life--;
        });
    }
    
    createParticles(x, y, color) {
        for (let i = 0; i < 15; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = 2 + Math.random() * 3;
            this.particles.push({
                x: x,
                y: y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                life: 40,
                color: color,
                size: 3 + Math.random() * 3
            });
        }
    }
    
    drawStar(x, y, radius, rotation) {
        const spikes = 5;
        const outerRadius = radius;
        const innerRadius = radius * 0.5;
        
        this.ctx.save();
        this.ctx.translate(x, y);
        this.ctx.rotate(rotation);
        this.ctx.beginPath();
        
        for (let i = 0; i < spikes * 2; i++) {
            const angle = (Math.PI / spikes) * i;
            const r = i % 2 === 0 ? outerRadius : innerRadius;
            const px = Math.cos(angle) * r;
            const py = Math.sin(angle) * r;
            
            if (i === 0) {
                this.ctx.moveTo(px, py);
            } else {
                this.ctx.lineTo(px, py);
            }
        }
        
        this.ctx.closePath();
        this.ctx.restore();
    }
    
    draw() {
        // Limpiar canvas
        this.ctx.fillStyle = '#0a0a1a';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Dibujar timer
        this.ctx.fillStyle = '#FFF';
        this.ctx.font = 'bold 24px Arial';
        this.ctx.textAlign = 'left';
        this.ctx.fillText(`⏱️ ${Math.ceil(this.timeLeft)}s`, 20, 40);
        
        // Dibujar estrellas
        this.stars.forEach(star => {
            const pulse = Math.sin(star.pulsePhase + Date.now() / 200) * 0.2 + 1;
            
            // Glow
            const gradient = this.ctx.createRadialGradient(star.x, star.y, 0, star.x, star.y, star.radius * pulse * 2);
            gradient.addColorStop(0, 'rgba(255, 215, 0, 0.3)');
            gradient.addColorStop(1, 'rgba(255, 215, 0, 0)');
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(star.x, star.y, star.radius * pulse * 2, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Estrella
            this.ctx.fillStyle = '#FFD700';
            this.drawStar(star.x, star.y, star.radius * pulse, star.rotation);
            this.ctx.fill();
            
            // Borde
            this.ctx.strokeStyle = '#FFF';
            this.ctx.lineWidth = 2;
            this.drawStar(star.x, star.y, star.radius * pulse, star.rotation);
            this.ctx.stroke();
            
            // Puntos
            this.ctx.fillStyle = '#000';
            this.ctx.font = 'bold 12px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(star.points, star.x, star.y);
        });
        
        // Dibujar obstáculos
        this.obstacles.forEach(obstacle => {
            this.ctx.save();
            this.ctx.translate(obstacle.x, obstacle.y);
            this.ctx.rotate(obstacle.rotation);
            
            // Hexágono
            this.ctx.fillStyle = '#ff5757';
            this.ctx.beginPath();
            for (let i = 0; i < 6; i++) {
                const angle = (Math.PI / 3) * i;
                const x = Math.cos(angle) * obstacle.radius;
                const y = Math.sin(angle) * obstacle.radius;
                if (i === 0) {
                    this.ctx.moveTo(x, y);
                } else {
                    this.ctx.lineTo(x, y);
                }
            }
            this.ctx.closePath();
            this.ctx.fill();
            
            this.ctx.strokeStyle = '#FFF';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            this.ctx.restore();
        });
        
        // Dibujar partículas
        this.particles.forEach(p => {
            this.ctx.fillStyle = p.color;
            this.ctx.globalAlpha = p.life / 40;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fill();
        });
        this.ctx.globalAlpha = 1;
        
        // Dibujar jugador
        const gradient = this.ctx.createRadialGradient(
            this.player.x, this.player.y, 0,
            this.player.x, this.player.y, this.player.radius
        );
        gradient.addColorStop(0, '#4CAF50');
        gradient.addColorStop(1, '#2E7D32');
        
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(this.player.x, this.player.y, this.player.radius, 0, Math.PI * 2);
        this.ctx.fill();
        
        this.ctx.strokeStyle = '#FFF';
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.arc(this.player.x, this.player.y, this.player.radius, 0, Math.PI * 2);
        this.ctx.stroke();
        
        // Instrucciones
        if (!this.running) {
            this.ctx.fillStyle = '#FFF';
            this.ctx.font = '20px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('Recoge las estrellas doradas ⭐', this.canvas.width / 2, 50);
            this.ctx.fillText('Evita los hexágonos rojos ⚠️', this.canvas.width / 2, 80);
        }
        
        // Game Over
        if (this.gameOver) {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            
            this.ctx.fillStyle = '#FFD700';
            this.ctx.font = 'bold 48px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('¡TIEMPO!', this.canvas.width / 2, this.canvas.height / 2 - 20);
            
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
                    <div style="color: #FFD700; font-size: 24px; margin-top: 20px;">
                        ¡Se acabó el tiempo! Puntuación: ${this.score}
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
        this.gameStartTime = Date.now();
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

window.EyeCollect = EyeCollect;
