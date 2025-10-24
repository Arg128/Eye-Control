// EyeGestures Minigames Integration - Integrated Version
// Este archivo maneja la integración directa en la página principal

// Eye Tracking Connection and Data Management
class EyeTrackingClient {
    constructor() {
        this.connected = false;
        this.gazeX = 0;
        this.gazeY = 0;
        this.fixation = 0;
        this.listeners = [];
        this.ws = null;
        this.fallbackMode = true; // Use mouse as fallback
        
        // Suavizado y filtrado
        this.gazeHistory = [];
        this.maxHistory = 8;  // Aumentado para mejor suavizado
        this.deadZone = 20;    // Zona muerta para reducir jitter
        this.lastX = 0;
        this.lastY = 0;
        
        // Calibración
        this.calibrating = false;
        this.calibrationProgress = 0;
        
        this.init();
    }

    init() {
        this.updateStatus('connecting');
        
        // Try to connect to WebSocket server
        this.connectWebSocket();
        
        // Fallback to mouse tracking
        if (this.fallbackMode) {
            this.setupMouseFallback();
        }
        
        // Start update loop
        this.startUpdateLoop();
    }

    connectWebSocket() {
        try {
            console.log('Attempting to connect to ws://localhost:8765...');
            this.ws = new WebSocket('ws://localhost:8765');
            
            this.ws.onopen = () => {
                console.log('✓ Connected to eye tracking server!');
                console.log('Waiting for calibration...');
                this.connected = true;
                this.fallbackMode = false;
                this.updateStatus('connected');
                
                // Send a ping to keep connection alive
                this.pingInterval = setInterval(() => {
                    if (this.ws.readyState === WebSocket.OPEN) {
                        this.ws.send(JSON.stringify({ type: 'ping' }));
                    }
                }, 5000);
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    
                    // Update gaze data con suavizado
                    if (data.x !== undefined && data.y !== undefined) {
                        // Agregar al historial
                        this.gazeHistory.push({
                            x: data.x,
                            y: data.y,
                            fixation: data.fixation || 0,
                            timestamp: Date.now()
                        });
                        
                        // Mantener solo los últimos N puntos
                        if (this.gazeHistory.length > this.maxHistory) {
                            this.gazeHistory.shift();
                        }
                        
                        // Calcular promedio ponderado (más peso a datos recientes)
                        let totalWeight = 0;
                        let weightedX = 0;
                        let weightedY = 0;
                        let weightedFixation = 0;
                        
                        this.gazeHistory.forEach((point, index) => {
                            const weight = index + 1; // Peso lineal creciente
                            weightedX += point.x * weight;
                            weightedY += point.y * weight;
                            weightedFixation += point.fixation * weight;
                            totalWeight += weight;
                        });
                        
                        let smoothedX = Math.round(weightedX / totalWeight);
                        let smoothedY = Math.round(weightedY / totalWeight);
                        
                        // Aplicar zona muerta para reducir jitter
                        const dx = Math.abs(smoothedX - this.lastX);
                        const dy = Math.abs(smoothedY - this.lastY);
                        
                        if (dx < this.deadZone && dy < this.deadZone && !data.calibrating) {
                            // Mantener posición anterior si el movimiento es muy pequeño
                            smoothedX = this.lastX;
                            smoothedY = this.lastY;
                        }
                        
                        this.gazeX = smoothedX;
                        this.gazeY = smoothedY;
                        this.fixation = weightedFixation / totalWeight;
                        this.lastX = smoothedX;
                        this.lastY = smoothedY;
                        
                        // Estado de calibración
                        this.calibrating = data.calibrating || false;
                        this.calibrationProgress = data.calibration_progress || 0;
                        
                        // Log calibration progress solo al principio
                        if (data.calibrating && data.calibration_progress % 10 === 0) {
                            console.log(`Calibrando: ${data.calibration_progress}/60 (${Math.round(data.calibration_progress/60*100)}%)`);
                        }
                        
                        // Notificar cuando termine calibración
                        if (!data.calibrating && this.calibrating) {
                            console.log('✓ Calibración completada! Sistema listo.');
                        }
                    }
                } catch (e) {
                    console.error('Error parsing message:', e);
                }
            };
            
            this.ws.onerror = (error) => {
                console.warn('WebSocket error:', error);
                console.log('Switching to mouse fallback mode');
                this.fallbackMode = true;
                this.updateStatus('disconnected');
            };
            
            this.ws.onclose = () => {
                console.log('Disconnected from eye tracking server');
                this.connected = false;
                this.fallbackMode = true;
                this.updateStatus('disconnected');
                
                // Clear ping interval
                if (this.pingInterval) {
                    clearInterval(this.pingInterval);
                }
                
                // Try to reconnect after 5 seconds
                console.log('Will attempt to reconnect in 5 seconds...');
                setTimeout(() => this.connectWebSocket(), 5000);
            };
        } catch (e) {
            console.error('WebSocket connection failed:', e);
            console.log('Using mouse fallback mode');
            this.fallbackMode = true;
            this.updateStatus('disconnected');
        }
    }

    setupMouseFallback() {
        document.addEventListener('mousemove', (e) => {
            if (this.fallbackMode) {
                this.gazeX = e.clientX;
                this.gazeY = e.clientY;
                this.fixation = 0.5; // Default fixation for mouse
            }
        });
        
        let clickTimeout = null;
        document.addEventListener('mousedown', () => {
            clickTimeout = setTimeout(() => {
                this.fixation = 1.0; // Simulate fixation on click hold
            }, 100);
        });
        
        document.addEventListener('mouseup', () => {
            if (clickTimeout) clearTimeout(clickTimeout);
            this.fixation = 0.5;
        });
    }

    updateStatus(status) {
        const statusElement = document.getElementById('connectionStatus');
        const indicatorElement = document.getElementById('connectionIndicator');
        const textElement = document.getElementById('connectionText');
        
        if (statusElement && indicatorElement && textElement) {
            switch (status) {
                case 'connected':
                    statusElement.className = 'connection-status connected';
                    indicatorElement.className = 'connection-indicator connected';
                    textElement.textContent = 'Eye Tracking Conectado';
                    break;
                case 'connecting':
                    statusElement.className = 'connection-status disconnected';
                    indicatorElement.className = 'connection-indicator disconnected';
                    textElement.textContent = 'Conectando...';
                    break;
                case 'disconnected':
                    statusElement.className = 'connection-status disconnected';
                    indicatorElement.className = 'connection-indicator disconnected';
                    textElement.textContent = 'Modo Mouse';
                    break;
            }
        }
    }

    startUpdateLoop() {
        setInterval(() => {
            // Update gaze cursor
            const cursor = document.getElementById('gazeCursor');
            if (cursor) {
                cursor.style.left = `${this.gazeX}px`;
                cursor.style.top = `${this.gazeY}px`;
                
                if (this.fixation > 0.7) {
                    cursor.classList.add('fixating');
                } else {
                    cursor.classList.remove('fixating');
                }
            }
            
            // Notify listeners
            this.notifyListeners();
        }, 16); // ~60 FPS
    }

    addListener(callback) {
        this.listeners.push(callback);
    }

    removeListener(callback) {
        this.listeners = this.listeners.filter(l => l !== callback);
    }

    notifyListeners() {
        const data = {
            x: this.gazeX,
            y: this.gazeY,
            fixation: this.fixation,
            timestamp: Date.now()
        };
        
        this.listeners.forEach(callback => {
            try {
                callback(data);
            } catch (e) {
                console.error('Error in listener:', e);
            }
        });
    }

    getGazeData() {
        return {
            x: this.gazeX,
            y: this.gazeY,
            fixation: this.fixation
        };
    }
}

// Create global instance
const eyeTracking = new EyeTrackingClient();

// Game Engine
class Game {
    constructor(canvas, title) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.title = title;
        this.score = 0;
        this.running = false;
        this.gazeListener = null;
    }

    start() {
        this.running = true;
        this.score = 0;
        this.updateScore();
        this.gameLoop();
    }

    stop() {
        this.running = false;
        if (this.gazeListener) {
            eyeTracking.removeListener(this.gazeListener);
        }
    }

    updateScore() {
        document.getElementById('gameScore').textContent = this.score;
    }

    gameLoop() {
        if (!this.running) return;
        this.update();
        this.draw();
        requestAnimationFrame(() => this.gameLoop());
    }

    update() {
        // Override in subclasses
    }

    draw() {
        // Override in subclasses
    }

    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}

// Aim Trainer Game
class AimTrainerGame extends Game {
    constructor(canvas) {
        super(canvas, 'Aim Trainer');
        this.targets = [];
        this.timeLeft = 60;
        this.targetRadius = 40;
        this.lastSpawn = 0;
    }

    start() {
        super.start();
        this.canvas.width = 1200;
        this.canvas.height = 700;
        this.spawnTarget();
        
        // Timer
        this.timerInterval = setInterval(() => {
            this.timeLeft--;
            if (this.timeLeft <= 0) {
                this.stop();
                this.showGameOver();
            }
        }, 1000);
        
        // Listen for gaze
        this.gazeListener = (data) => {
            this.checkHit(data.x - this.canvas.offsetLeft, data.y - this.canvas.offsetTop, data.fixation);
        };
        eyeTracking.addListener(this.gazeListener);
    }

    spawnTarget() {
        const padding = this.targetRadius + 20;
        this.targets.push({
            x: padding + Math.random() * (this.canvas.width - padding * 2),
            y: padding + Math.random() * (this.canvas.height - padding * 2),
            radius: this.targetRadius,
            createdAt: Date.now(),
            gazeDuration: 0
        });
    }

    checkHit(gazeX, gazeY, fixation) {
        this.targets.forEach((target, index) => {
            const dx = gazeX - target.x;
            const dy = gazeY - target.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < target.radius) {
                target.gazeDuration += 16; // ~16ms per frame
                
                if (target.gazeDuration > 500) { // 0.5 second fixation
                    this.score += 10;
                    this.updateScore();
                    this.targets.splice(index, 1);
                    this.spawnTarget();
                }
            } else {
                target.gazeDuration = 0;
            }
        });
    }

    update() {
        // Remove old targets
        const now = Date.now();
        this.targets = this.targets.filter(t => now - t.createdAt < 3000);
        
        // Spawn new target if needed
        if (this.targets.length < 3) {
            this.spawnTarget();
        }
    }

    draw() {
        this.clear();
        
        // Background
        this.ctx.fillStyle = '#111827';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw targets
        this.targets.forEach(target => {
            // Outer ring (progress)
            const progress = target.gazeDuration / 500;
            this.ctx.beginPath();
            this.ctx.arc(target.x, target.y, target.radius + 10, 0, Math.PI * 2 * progress);
            this.ctx.strokeStyle = '#22c55e';
            this.ctx.lineWidth = 5;
            this.ctx.stroke();
            
            // Main target
            const gradient = this.ctx.createRadialGradient(
                target.x, target.y, 0,
                target.x, target.y, target.radius
            );
            gradient.addColorStop(0, '#ef4444');
            gradient.addColorStop(1, '#991b1b');
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(target.x, target.y, target.radius, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Center dot
            this.ctx.fillStyle = '#ffffff';
            this.ctx.beginPath();
            this.ctx.arc(target.x, target.y, 8, 0, Math.PI * 2);
            this.ctx.fill();
        });
        
        // Draw timer
        this.ctx.fillStyle = '#f3f4f6';
        this.ctx.font = 'bold 32px Arial';
        this.ctx.fillText(`Tiempo: ${this.timeLeft}s`, 20, 40);
    }

    stop() {
        super.stop();
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
    }

    showGameOver() {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = '#f3f4f6';
        this.ctx.font = 'bold 48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('¡Juego Terminado!', this.canvas.width / 2, this.canvas.height / 2 - 50);
        
        this.ctx.font = 'bold 36px Arial';
        this.ctx.fillStyle = '#22c55e';
        this.ctx.fillText(`Puntuación Final: ${this.score}`, this.canvas.width / 2, this.canvas.height / 2 + 20);
    }
}

// Memory Game
class MemoryGame extends Game {
    constructor(canvas) {
        super(canvas, 'Memory Match');
        this.cards = [];
        this.flippedCards = [];
        this.matchedPairs = 0;
        this.gridSize = 4;
        this.cardSize = 100;
        this.gap = 20;
    }

    start() {
        super.start();
        this.canvas.width = 1200;
        this.canvas.height = 700;
        this.initCards();
        
        this.gazeListener = (data) => {
            this.checkCardClick(data.x - this.canvas.offsetLeft, data.y - this.canvas.offsetTop, data.fixation);
        };
        eyeTracking.addListener(this.gazeListener);
    }

    initCards() {
        const emojis = ['🎯', '🎮', '🌟', '🚀', '💎', '🎨', '🎪', '🎭'];
        const pairs = [...emojis, ...emojis];
        pairs.sort(() => Math.random() - 0.5);
        
        const startX = (this.canvas.width - (this.gridSize * (this.cardSize + this.gap) - this.gap)) / 2;
        const startY = (this.canvas.height - (this.gridSize * (this.cardSize + this.gap) - this.gap)) / 2;
        
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                this.cards.push({
                    x: startX + j * (this.cardSize + this.gap),
                    y: startY + i * (this.cardSize + this.gap),
                    width: this.cardSize,
                    height: this.cardSize,
                    emoji: pairs[i * this.gridSize + j],
                    flipped: false,
                    matched: false,
                    gazeDuration: 0
                });
            }
        }
    }

    checkCardClick(gazeX, gazeY, fixation) {
        if (this.flippedCards.length >= 2) return;
        
        this.cards.forEach(card => {
            if (card.matched || card.flipped) return;
            
            if (gazeX >= card.x && gazeX <= card.x + card.width &&
                gazeY >= card.y && gazeY <= card.y + card.height) {
                card.gazeDuration += 16;
                
                if (card.gazeDuration > 800) { // 0.8 second to flip
                    card.flipped = true;
                    card.gazeDuration = 0;
                    this.flippedCards.push(card);
                    
                    if (this.flippedCards.length === 2) {
                        setTimeout(() => this.checkMatch(), 1000);
                    }
                }
            } else {
                card.gazeDuration = 0;
            }
        });
    }

    checkMatch() {
        const [card1, card2] = this.flippedCards;
        
        if (card1.emoji === card2.emoji) {
            card1.matched = true;
            card2.matched = true;
            this.matchedPairs++;
            this.score += 20;
            this.updateScore();
            
            if (this.matchedPairs === this.cards.length / 2) {
                setTimeout(() => this.showWin(), 500);
            }
        } else {
            card1.flipped = false;
            card2.flipped = false;
        }
        
        this.flippedCards = [];
    }

    draw() {
        this.clear();
        
        this.ctx.fillStyle = '#111827';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.cards.forEach(card => {
            // Card background
            if (card.matched) {
                this.ctx.fillStyle = '#22c55e';
            } else if (card.flipped) {
                this.ctx.fillStyle = '#2d55ff';
            } else {
                this.ctx.fillStyle = '#1f2937';
            }
            
            this.ctx.fillRect(card.x, card.y, card.width, card.height);
            this.ctx.strokeStyle = '#6366f1';
            this.ctx.lineWidth = 3;
            this.ctx.strokeRect(card.x, card.y, card.width, card.height);
            
            // Progress indicator
            if (!card.matched && !card.flipped && card.gazeDuration > 0) {
                const progress = card.gazeDuration / 800;
                this.ctx.fillStyle = 'rgba(34, 197, 94, 0.5)';
                this.ctx.fillRect(card.x, card.y + card.height - 10, card.width * progress, 10);
            }
            
            // Content
            if (card.flipped || card.matched) {
                this.ctx.font = '48px Arial';
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText(card.emoji, card.x + card.width / 2, card.y + card.height / 2);
            } else {
                this.ctx.fillStyle = '#6366f1';
                this.ctx.font = 'bold 32px Arial';
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText('?', card.x + card.width / 2, card.y + card.height / 2);
            }
        });
    }

    showWin() {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = '#22c55e';
        this.ctx.font = 'bold 48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('¡Ganaste! 🎉', this.canvas.width / 2, this.canvas.height / 2);
    }
}

// Snake Game
class SnakeEyeGame extends Game {
    constructor(canvas) {
        super(canvas, 'Snake Eye');
        this.snake = [{ x: 300, y: 300 }];
        this.direction = { x: 0, y: 0 };
        this.food = { x: 0, y: 0 };
        this.gridSize = 20;
        this.lastMove = 0;
        this.moveInterval = 150;
        this.gazeThreshold = 100;
    }

    start() {
        super.start();
        this.canvas.width = 1200;
        this.canvas.height = 700;
        this.spawnFood();
        
        this.gazeListener = (data) => {
            this.updateDirection(data.x - this.canvas.offsetLeft, data.y - this.canvas.offsetTop);
        };
        eyeTracking.addListener(this.gazeListener);
    }

    updateDirection(gazeX, gazeY) {
        const canvas = this.canvas;
        
        if (gazeX < this.gazeThreshold) {
            this.direction = { x: -1, y: 0 };
        } else if (gazeX > canvas.width - this.gazeThreshold) {
            this.direction = { x: 1, y: 0 };
        } else if (gazeY < this.gazeThreshold) {
            this.direction = { x: 0, y: -1 };
        } else if (gazeY > canvas.height - this.gazeThreshold) {
            this.direction = { x: 0, y: 1 };
        }
    }

    spawnFood() {
        const maxX = Math.floor(this.canvas.width / this.gridSize);
        const maxY = Math.floor(this.canvas.height / this.gridSize);
        
        this.food = {
            x: Math.floor(Math.random() * maxX) * this.gridSize,
            y: Math.floor(Math.random() * maxY) * this.gridSize
        };
        
        for (let segment of this.snake) {
            if (segment.x === this.food.x && segment.y === this.food.y) {
                this.spawnFood();
                return;
            }
        }
    }

    update() {
        const now = Date.now();
        if (now - this.lastMove < this.moveInterval) return;
        
        this.lastMove = now;
        
        const head = { ...this.snake[0] };
        head.x += this.direction.x * this.gridSize;
        head.y += this.direction.y * this.gridSize;
        
        if (head.x < 0 || head.x >= this.canvas.width || 
            head.y < 0 || head.y >= this.canvas.height) {
            this.gameOver();
            return;
        }
        
        for (let segment of this.snake) {
            if (head.x === segment.x && head.y === segment.y) {
                this.gameOver();
                return;
            }
        }
        
        this.snake.unshift(head);
        
        if (head.x === this.food.x && head.y === this.food.y) {
            this.score += 10;
            this.updateScore();
            this.spawnFood();
        } else {
            this.snake.pop();
        }
    }

    draw() {
        this.clear();
        
        this.ctx.fillStyle = '#111827';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.snake.forEach((segment, index) => {
            if (index === 0) {
                this.ctx.fillStyle = '#22c55e';
            } else {
                this.ctx.fillStyle = '#16a34a';
            }
            
            this.ctx.fillRect(segment.x, segment.y, this.gridSize - 2, this.gridSize - 2);
            
            this.ctx.strokeStyle = '#15803d';
            this.ctx.lineWidth = 1;
            this.ctx.strokeRect(segment.x, segment.y, this.gridSize - 2, this.gridSize - 2);
        });
        
        this.ctx.fillStyle = '#ef4444';
        this.ctx.beginPath();
        this.ctx.arc(
            this.food.x + this.gridSize / 2, 
            this.food.y + this.gridSize / 2, 
            this.gridSize / 2 - 2, 
            0, 
            Math.PI * 2
        );
        this.ctx.fill();
        
        this.ctx.fillStyle = '#f3f4f6';
        this.ctx.font = 'bold 20px Arial';
        this.ctx.fillText('Mira hacia los bordes para cambiar dirección', 20, 30);
        this.ctx.fillText(`Puntuación: ${this.score}`, 20, 60);
    }

    gameOver() {
        this.stop();
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = '#ef4444';
        this.ctx.font = 'bold 48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('¡Game Over!', this.canvas.width / 2, this.canvas.height / 2 - 50);
        
        this.ctx.font = 'bold 36px Arial';
        this.ctx.fillStyle = '#22c55e';
        this.ctx.fillText(`Puntuación Final: ${this.score}`, this.canvas.width / 2, this.canvas.height / 2 + 20);
    }
}

// Bubble Pop Game
class BubblePopGame extends Game {
    constructor(canvas) {
        super(canvas, 'Bubble Pop');
        this.bubbles = [];
        this.maxBubbles = 8;
    }

    start() {
        super.start();
        this.canvas.width = 1200;
        this.canvas.height = 700;
        
        this.gazeListener = (data) => {
            this.checkBubblePop(data.x - this.canvas.offsetLeft, data.y - this.canvas.offsetTop, data.fixation);
        };
        eyeTracking.addListener(this.gazeListener);
    }

    update() {
        while (this.bubbles.length < this.maxBubbles) {
            this.bubbles.push({
                x: 50 + Math.random() * (this.canvas.width - 100),
                y: this.canvas.height + 50,
                radius: 30 + Math.random() * 30,
                speed: 0.5 + Math.random() * 1.5,
                color: `hsl(${Math.random() * 360}, 70%, 60%)`,
                gazeDuration: 0
            });
        }
        
        this.bubbles.forEach(bubble => {
            bubble.y -= bubble.speed;
        });
        
        this.bubbles = this.bubbles.filter(b => b.y > -100);
    }

    checkBubblePop(gazeX, gazeY, fixation) {
        this.bubbles.forEach((bubble, index) => {
            const dx = gazeX - bubble.x;
            const dy = gazeY - bubble.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < bubble.radius) {
                bubble.gazeDuration += 16;
                
                if (bubble.gazeDuration > 1000) {
                    this.score += Math.floor(bubble.radius / 10);
                    this.updateScore();
                    this.bubbles.splice(index, 1);
                }
            } else {
                bubble.gazeDuration = 0;
            }
        });
    }

    draw() {
        this.clear();
        
        this.ctx.fillStyle = '#111827';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.bubbles.forEach(bubble => {
            const gradient = this.ctx.createRadialGradient(
                bubble.x - bubble.radius / 3, bubble.y - bubble.radius / 3, 0,
                bubble.x, bubble.y, bubble.radius
            );
            gradient.addColorStop(0, bubble.color);
            gradient.addColorStop(0.7, bubble.color);
            gradient.addColorStop(1, 'rgba(255, 255, 255, 0.2)');
            
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(bubble.x, bubble.y, bubble.radius, 0, Math.PI * 2);
            this.ctx.fill();
            
            if (bubble.gazeDuration > 0) {
                const progress = bubble.gazeDuration / 1000;
                this.ctx.beginPath();
                this.ctx.arc(bubble.x, bubble.y, bubble.radius + 5, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * progress);
                this.ctx.strokeStyle = '#22c55e';
                this.ctx.lineWidth = 4;
                this.ctx.stroke();
            }
        });
    }
}

// Game Registry
const games = {
    'aimTrainer': AimTrainerGame,
    'memoryGame': MemoryGame,
    'snakeGame': SnakeEyeGame,
    'bubblePop': BubblePopGame
};

// Game Management
let currentGame = null;
let gameInstructions = {
    'aimTrainer': '🎯 <strong>Aim Trainer:</strong><br/>• <span class="eye-mode">Con Eye Tracking:</span> Mira a los objetivos rojos y mantén la fijación durante 0.5 segundos para destruirlos<br/>• <span class="mouse-mode">Con Mouse:</span> Mueve el mouse sobre los objetivos y mantén presionado durante 0.5 segundos<br/>• ¡Consigue la mayor puntuación en 60 segundos!',
    'memoryGame': '🧠 <strong>Memory Match:</strong><br/>• <span class="eye-mode">Con Eye Tracking:</span> Mira a las cartas y mantén la fijación durante 0.8 segundos para voltearlas<br/>• <span class="mouse-mode">Con Mouse:</span> Haz clic y mantén presionado sobre las cartas durante 0.8 segundos<br/>• Encuentra todas las parejas para ganar',
    'snakeGame': '🐍 <strong>Snake Eye:</strong><br/>• <span class="eye-mode">Con Eye Tracking:</span> Mira hacia los bordes de la pantalla para cambiar la dirección<br/>• <span class="mouse-mode">Con Mouse:</span> Mueve el mouse hacia los bordes de la pantalla para cambiar dirección<br/>• Evita chocar con las paredes y tu propio cuerpo',
    'bubblePop': '💫 <strong>Bubble Pop:</strong><br/>• <span class="eye-mode">Con Eye Tracking:</span> Mira a las burbujas y mantén la fijación durante 1 segundo<br/>• <span class="mouse-mode">Con Mouse:</span> Mueve el mouse sobre las burbujas y mantén presionado durante 1 segundo<br/>• ¡Las burbujas más grandes dan más puntos!'
};

// Main Integration Class
class MinigamesIntegration {
    constructor() {
        this.gameInfo = {
            'aimTrainer': {
                title: 'Aim Trainer',
                description: 'Entrena tu precisión apuntando a objetivos que aparecen en pantalla. Usa tu mirada para apuntar y mantener la fijación durante 0.5 segundos para destruir cada objetivo.',
                difficulty: 'Fácil',
                duration: '60 segundos',
                controls: 'Control por mirada',
                icon: '🎯',
                features: ['Objetivos dinámicos', 'Sistema de puntuación', 'Temporizador']
            },
            'memoryGame': {
                title: 'Memory Match',
                description: 'Encuentra las parejas de cartas usando solo tu mirada. Mantén la fijación en cada carta durante 0.8 segundos para voltearla.',
                difficulty: 'Medio',
                duration: 'Variable',
                controls: 'Control por mirada',
                icon: '🧠',
                features: ['16 cartas', 'Sistema de memoria', 'Detección de parejas']
            },
            'snakeGame': {
                title: 'Snake Eye',
                description: 'Clásico juego Snake controlado con la dirección de tu mirada. Dirige la serpiente mirando hacia los bordes de la pantalla.',
                difficulty: 'Difícil',
                duration: 'Infinito',
                controls: 'Control por mirada',
                icon: '🐍',
                features: ['Control direccional', 'Crecimiento progresivo', 'Detección de colisiones']
            },
            'bubblePop': {
                title: 'Bubble Pop',
                description: 'Revienta burbujas mirándolas durante 1 segundo. Las burbujas aparecen desde abajo y suben por la pantalla.',
                difficulty: 'Fácil',
                duration: 'Infinito',
                controls: 'Control por mirada',
                icon: '💫',
                features: ['Burbujas dinámicas', 'Efectos visuales', 'Sistema de puntuación']
            }
        };
        
        this.init();
    }

    init() {
        this.addEventListeners();
        this.addHoverEffects();
    }

    // Función principal para cargar minijuegos
    loadMinigame(gameName) {
        if (!this.gameInfo[gameName]) {
            console.error('Juego no encontrado:', gameName);
            return;
        }

        // Mostrar modal de confirmación
        this.showGameModal(gameName);
    }

    // Mostrar modal con información del juego
    showGameModal(gameName) {
        const info = this.gameInfo[gameName];
        
        // Crear modal dinámicamente
        const modal = document.createElement('div');
        modal.className = 'minigame-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${info.icon} ${info.title}</h2>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <p class="game-description">${info.description}</p>
                    <div class="game-details">
                        <div class="detail-item">
                            <strong>Dificultad:</strong> ${info.difficulty}
                        </div>
                        <div class="detail-item">
                            <strong>Duración:</strong> ${info.duration}
                        </div>
                        <div class="detail-item">
                            <strong>Controles:</strong> ${info.controls}
                        </div>
                    </div>
                    <div class="game-features">
                        <h4>Características:</h4>
                        <ul>
                            ${info.features.map(feature => `<li>${feature}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="minigamesIntegration.closeModal()">Cancelar</button>
                    <button class="btn-primary" onclick="minigamesIntegration.startGame('${gameName}')">Jugar Ahora</button>
                </div>
            </div>
        `;

        // Agregar estilos del modal
        this.addModalStyles();
        
        // Agregar modal al DOM
        document.body.appendChild(modal);
        
        // Event listeners para cerrar modal
        modal.querySelector('.close-modal').addEventListener('click', () => this.closeModal());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.closeModal();
        });
    }

    // Iniciar el juego directamente en overlay
    startGame(gameName) {
        this.closeModal();
        
        const GameClass = games[gameName];
        if (!GameClass) {
            alert('Este juego aún no está disponible. ¡Próximamente!');
            return;
        }
        
        // Bloquear scroll del body
        document.body.classList.add('game-active');
        
        // Mostrar overlay
        const overlay = document.getElementById('gameOverlay');
        overlay.classList.add('active');
        
        // Set game title and instructions
        document.getElementById('currentGameTitle').textContent = GameClass.name || gameName;
        
        // Set instructions with proper HTML rendering
        const instructionElement = document.getElementById('instructionText');
        instructionElement.innerHTML = gameInstructions[gameName] || 'Usa tu mirada para controlar el juego';
        
        // Initialize game
        const canvas = document.getElementById('gameCanvas');
        currentGame = new GameClass(canvas);
        currentGame.start();
    }

    // Cerrar modal
    closeModal() {
        const modal = document.querySelector('.minigame-modal');
        if (modal) {
            modal.remove();
        }
    }

    // Cerrar juego
    closeGame() {
        // Stop current game
        if (currentGame) {
            currentGame.stop();
            currentGame = null;
        }
        
        // Restaurar scroll del body
        document.body.classList.remove('game-active');
        
        // Hide game overlay
        const overlay = document.getElementById('gameOverlay');
        overlay.classList.remove('active');
    }

    // Agregar efectos hover a las tarjetas de juego
    addHoverEffects() {
        document.addEventListener('DOMContentLoaded', () => {
            const gameCards = document.querySelectorAll('.event__item');
            gameCards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-8px) scale(1.02)';
                    this.style.transition = 'all 0.3s ease';
                    this.style.boxShadow = '0 15px 40px rgba(0, 0, 0, 0.4)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0) scale(1)';
                    this.style.boxShadow = '';
                });
            });
        });
    }

    // Agregar event listeners
    addEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            // Agregar click listeners a las tarjetas de juego
            const gameCards = document.querySelectorAll('.event__item[onclick]');
            gameCards.forEach(card => {
                const onclick = card.getAttribute('onclick');
                if (onclick && onclick.includes('loadMinigame')) {
                    card.addEventListener('click', (e) => {
                        e.preventDefault();
                        const gameName = onclick.match(/'([^']+)'/)[1];
                        this.loadMinigame(gameName);
                    });
                }
            });
        });
    }

    // Agregar estilos CSS para el modal
    addModalStyles() {
        if (document.getElementById('minigame-modal-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'minigame-modal-styles';
        styles.textContent = `
            .minigame-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10000;
                animation: fadeIn 0.3s ease;
            }
            
            .modal-content {
                background: #1a1a1a;
                border-radius: 15px;
                max-width: 500px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                animation: slideIn 0.3s ease;
            }
            
            .modal-header {
                padding: 20px;
                border-bottom: 1px solid #333;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-header h2 {
                color: #fff;
                margin: 0;
                font-size: 24px;
            }
            
            .close-modal {
                background: none;
                border: none;
                color: #fff;
                font-size: 24px;
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .close-modal:hover {
                color: #6366f1;
            }
            
            .modal-body {
                padding: 20px;
            }
            
            .game-description {
                color: #ccc;
                line-height: 1.6;
                margin-bottom: 20px;
            }
            
            .game-details {
                margin-bottom: 20px;
            }
            
            .detail-item {
                color: #fff;
                margin-bottom: 8px;
            }
            
            .detail-item strong {
                color: #6366f1;
            }
            
            .game-features h4 {
                color: #fff;
                margin-bottom: 10px;
            }
            
            .game-features ul {
                color: #ccc;
                padding-left: 20px;
            }
            
            .game-features li {
                margin-bottom: 5px;
            }
            
            .modal-footer {
                padding: 20px;
                border-top: 1px solid #333;
                display: flex;
                gap: 10px;
                justify-content: flex-end;
            }
            
            .btn-primary, .btn-secondary {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            
            .btn-primary {
                background: #6366f1;
                color: #fff;
            }
            
            .btn-primary:hover {
                background: #4f46e5;
                transform: translateY(-2px);
            }
            
            .btn-secondary {
                background: #333;
                color: #fff;
            }
            
            .btn-secondary:hover {
                background: #555;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes slideIn {
                from { transform: translateY(-50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
        `;
        
        document.head.appendChild(styles);
    }
}

// Inicializar la integración cuando se carga la página
let minigamesIntegration;
document.addEventListener('DOMContentLoaded', () => {
    minigamesIntegration = new MinigamesIntegration();
    console.log('EyeMotion Minigames Integration loaded successfully!');
    console.log('Eye tracking system initialized - attempting connection to ws://localhost:8765');
    
    // Agregar event listeners para cerrar el juego
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && currentGame) {
            minigamesIntegration.closeGame();
        }
    });
    
    // Cerrar juego al hacer clic fuera del contenedor
    document.addEventListener('click', (e) => {
        const overlay = document.getElementById('gameOverlay');
        if (overlay && overlay.classList.contains('active')) {
            if (e.target === overlay) {
                minigamesIntegration.closeGame();
            }
        }
    });
});

// Función global para cerrar juego
function closeGame() {
    if (minigamesIntegration) {
        minigamesIntegration.closeGame();
    }
}

// Función global para compatibilidad con onclick
function loadMinigame(gameName) {
    if (minigamesIntegration) {
        minigamesIntegration.loadMinigame(gameName);
    }
}