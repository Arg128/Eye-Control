/**
 * Eye Target - Juego de disparar objetivos mirándolos
 */

class EyeTarget {
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
        
        // Cursor de la mirada
        this.gaze = {
            x: this.canvas.width / 2,
            y: this.canvas.height / 2,
            radius: 20,
            dwellTime: 0,
            dwellRequired: 1000 // 1 segundo mirando para disparar
        };
        
        // Objetivos
        this.targets = [];
        this.maxTargets = 5;
        this.targetSpawnInterval = 2000;
        this.lastSpawn = Date.now();
        
        // Efectos
        this.explosions = [];
        
        this.init();
    }
    
    init() {
        this.spawnTarget();
    }
    
    spawnTarget() {
        const margin = 50;
        const target = {
            x: margin + Math.random() * (this.canvas.width - margin * 2),
            y: margin + Math.random() * (this.canvas.height - margin * 2),
            radius: 30 + Math.random() * 20,
            speed: 0.5 + Math.random() * 1.5,
            angle: Math.random() * Math.PI * 2,
            points: Math.floor(10 + Math.random() * 40),
            color: this.getRandomColor(),
            life: 100,
            maxLife: 100
        };
        
        this.targets.push(target);
    }
    
    getRandomColor() {
        const colors = ['#ff5757', '#4CAF50', '#2196F3', '#FFC107', '#9C27B0', '#FF6F00'];
        return colors[Math.floor(Math.random() * colors.length)];
    }
    
    onGaze(x, y) {
        const canvasRect = this.canvas.getBoundingClientRect();
        this.gaze.x = x - canvasRect.left;
        this.gaze.y = y - canvasRect.top;
        
        // Verificar si está mirando un objetivo
        let lookingAtTarget = false;
        
        this.targets.forEach(target => {
            const dist = Math.hypot(this.gaze.x - target.x, this.gaze.y - target.y);
            if (dist < target.radius + this.gaze.radius) {
                lookingAtTarget = true;
                target.isLookedAt = true;
            } else {
                target.isLookedAt = false;
            }
        });
        
        // Incrementar tiempo de mirada si está mirando un objetivo
        if (lookingAtTarget) {
            this.gaze.dwellTime += 16; // Aproximadamente 1 frame a 60fps
        } else {
            this.gaze.dwellTime = 0;
        }
    }
    
    update() {
        if (this.gameOver) return;
        
        const now = Date.now();
        
        // Spawn nuevos objetivos
        if (this.targets.length < this.maxTargets && now - this.lastSpawn > this.targetSpawnInterval) {
            this.spawnTarget();
            this.lastSpawn = now;
        }
        
        // Actualizar objetivos
        this.targets.forEach(target => {
            // Mover objetivo
            target.x += Math.cos(target.angle) * target.speed;
            target.y += Math.sin(target.angle) * target.speed;
            
            // Rebotar en bordes
            if (target.x - target.radius < 0 || target.x + target.radius > this.canvas.width) {
                target.angle = Math.PI - target.angle;
            }
            if (target.y - target.radius < 0 || target.y + target.radius > this.canvas.height) {
                target.angle = -target.angle;
            }
            
            // Mantener dentro del canvas
            target.x = Math.max(target.radius, Math.min(this.canvas.width - target.radius, target.x));
            target.y = Math.max(target.radius, Math.min(this.canvas.height - target.radius, target.y));
            
            // Reducir vida con el tiempo
            target.life -= 0.1;
        });
        
        // Verificar si se completó el dwell time (mirada sostenida)
        if (this.gaze.dwellTime >= this.gaze.dwellRequired) {
            this.targets.forEach((target, index) => {
                if (target.isLookedAt) {
                    // Destruir objetivo
                    this.score += target.points;
                    this.updateScore();
                    this.createExplosion(target.x, target.y, target.color);
                    this.targets.splice(index, 1);
                }
            });
            this.gaze.dwellTime = 0;
        }
        
        // Eliminar objetivos sin vida
        this.targets = this.targets.filter(t => t.life > 0);
        
        // Actualizar explosiones
        this.explosions = this.explosions.filter(e => e.life > 0);
        this.explosions.forEach(e => {
            e.particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.2; // Gravedad
            });
            e.life--;
        });
    }
    
    createExplosion(x, y, color) {
        const particles = [];
        for (let i = 0; i < 20; i++) {
            const angle = (Math.PI * 2 * i) / 20;
            const speed = 2 + Math.random() * 4;
            particles.push({
                x: x,
                y: y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                radius: 3 + Math.random() * 3
            });
        }
        
        this.explosions.push({
            particles: particles,
            color: color,
            life: 60
        });
    }
    
    draw() {
        // Limpiar canvas
        this.ctx.fillStyle = '#0f0f1e';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Dibujar objetivos
        this.targets.forEach(target => {
            // Sombra si está siendo mirado
            if (target.isLookedAt) {
                this.ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                this.ctx.beginPath();
                this.ctx.arc(target.x, target.y, target.radius + 10, 0, Math.PI * 2);
                this.ctx.fill();
            }
            
            // Objetivo
            this.ctx.fillStyle = target.color;
            this.ctx.beginPath();
            this.ctx.arc(target.x, target.y, target.radius, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Borde
            this.ctx.strokeStyle = '#FFF';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(target.x, target.y, target.radius, 0, Math.PI * 2);
            this.ctx.stroke();
            
            // Puntos
            this.ctx.fillStyle = '#FFF';
            this.ctx.font = 'bold 16px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(target.points, target.x, target.y);
            
            // Barra de vida
            const barWidth = target.radius * 2;
            const barHeight = 5;
            const barX = target.x - target.radius;
            const barY = target.y + target.radius + 10;
            
            this.ctx.fillStyle = '#333';
            this.ctx.fillRect(barX, barY, barWidth, barHeight);
            this.ctx.fillStyle = '#4CAF50';
            this.ctx.fillRect(barX, barY, barWidth * (target.life / target.maxLife), barHeight);
        });
        
        // Dibujar explosiones
        this.explosions.forEach(e => {
            e.particles.forEach(p => {
                this.ctx.fillStyle = e.color;
                this.ctx.globalAlpha = e.life / 60;
                this.ctx.beginPath();
                this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                this.ctx.fill();
            });
        });
        this.ctx.globalAlpha = 1;
        
        // Cursor de mirada
        this.ctx.strokeStyle = '#FFD700';
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.arc(this.gaze.x, this.gaze.y, this.gaze.radius, 0, Math.PI * 2);
        this.ctx.stroke();
        
        // Indicador de dwell time (progreso de mirada)
        if (this.gaze.dwellTime > 0) {
            const progress = this.gaze.dwellTime / this.gaze.dwellRequired;
            this.ctx.strokeStyle = '#4CAF50';
            this.ctx.lineWidth = 5;
            this.ctx.beginPath();
            this.ctx.arc(
                this.gaze.x, 
                this.gaze.y, 
                this.gaze.radius + 5, 
                -Math.PI / 2, 
                -Math.PI / 2 + (Math.PI * 2 * progress)
            );
            this.ctx.stroke();
        }
        
        // Instrucciones
        if (!this.running) {
            this.ctx.fillStyle = '#FFF';
            this.ctx.font = '24px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('Mira los objetivos durante 1 segundo para destruirlos', this.canvas.width / 2, 50);
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

window.EyeTarget = EyeTarget;
