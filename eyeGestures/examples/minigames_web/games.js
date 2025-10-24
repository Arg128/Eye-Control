// Game Engine and Minigames Implementation
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

// 1. Aim Trainer Game
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

// 2. Memory Match Game
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

// 3. Bubble Pop Game
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
        // Spawn new bubbles
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
        
        // Update bubble positions
        this.bubbles.forEach(bubble => {
            bubble.y -= bubble.speed;
        });
        
        // Remove off-screen bubbles
        this.bubbles = this.bubbles.filter(b => b.y > -100);
    }

    checkBubblePop(gazeX, gazeY, fixation) {
        this.bubbles.forEach((bubble, index) => {
            const dx = gazeX - bubble.x;
            const dy = gazeY - bubble.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < bubble.radius) {
                bubble.gazeDuration += 16;
                
                if (bubble.gazeDuration > 1000) { // 1 second to pop
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
            // Bubble
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
            
            // Progress ring
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
    'bubblePop': BubblePopGame,
    'snakeGame': null, // TODO
    'reactionTest': null, // TODO
    'focusFlow': null // TODO
};
