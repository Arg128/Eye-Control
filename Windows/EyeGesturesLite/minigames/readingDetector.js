// Detector de lectura - Analiza patrones de movimiento ocular para detectar lectura
class ReadingDetector {
    constructor(options = {}) {
        this.enabled = options.enabled !== undefined ? options.enabled : true;
        this.minReadingTime = options.minReadingTime || 2000; // 2 segundos mínimo
        this.maxSaccadeDistance = options.maxSaccadeDistance || 300; // Distancia máxima de salto
        this.lineThreshold = options.lineThreshold || 50; // Umbral para detectar cambio de línea
        
        this.gazeHistory = [];
        this.maxHistorySize = 30;
        this.isReading = false;
        this.readingStartTime = null;
        this.currentLine = null;
        this.lineChanges = 0;
        this.leftToRightMovements = 0;
        this.totalMovements = 0;
        
        // Estadísticas
        this.stats = {
            totalReadingTime: 0,
            linesRead: 0,
            wordsPerMinute: 0,
            lastUpdate: Date.now()
        };
        
        // Callbacks
        this.onReadingStart = options.onReadingStart || (() => {});
        this.onReadingEnd = options.onReadingEnd || (() => {});
        this.onStatsUpdate = options.onStatsUpdate || (() => {});
        
        this.createUI();
    }
    
    createUI() {
        // Panel de estadísticas de lectura
        const panel = document.createElement('div');
        panel.id = 'reading-detector-panel';
        panel.style.position = 'fixed';
        panel.style.top = '120px';
        panel.style.right = '20px';
        panel.style.background = 'rgba(0, 0, 0, 0.8)';
        panel.style.color = 'white';
        panel.style.padding = '15px';
        panel.style.borderRadius = '10px';
        panel.style.fontFamily = 'Arial, sans-serif';
        panel.style.fontSize = '14px';
        panel.style.zIndex = '9999';
        panel.style.minWidth = '200px';
        panel.style.display = 'none';
        
        panel.innerHTML = `
            <h3 style="margin: 0 0 10px 0; font-size: 16px;">📖 Modo Lectura</h3>
            <div class="reading-stat">
                <span>Estado:</span>
                <span id="reading-status" style="font-weight: bold; color: #4CAF50;">Detectando...</span>
            </div>
            <div class="reading-stat">
                <span>Tiempo leyendo:</span>
                <span id="reading-time">0s</span>
            </div>
            <div class="reading-stat">
                <span>Líneas leídas:</span>
                <span id="lines-read">0</span>
            </div>
            <div class="reading-stat">
                <span>Palabras/min:</span>
                <span id="words-per-minute">0</span>
            </div>
            <div class="reading-stat">
                <span>Patrón:</span>
                <span id="reading-pattern">--</span>
            </div>
            <style>
                .reading-stat {
                    display: flex;
                    justify-content: space-between;
                    margin: 5px 0;
                    padding: 3px 0;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
            </style>
        `;
        
        document.body.appendChild(panel);
        this.panel = panel;
    }
    
    addGazePoint(x, y) {
        if (!this.enabled) return;
        
        const point = { x, y, timestamp: Date.now() };
        this.gazeHistory.push(point);
        
        // Limitar historial
        if (this.gazeHistory.length > this.maxHistorySize) {
            this.gazeHistory.shift();
        }
        
        // Analizar patrón si tenemos suficientes puntos
        if (this.gazeHistory.length >= 5) {
            this.analyzePattern();
        }
        
        this.updateUI();
    }
    
    analyzePattern() {
        if (this.gazeHistory.length < 5) return;
        
        // Analizar últimos 5 puntos
        const recentPoints = this.gazeHistory.slice(-5);
        
        // Detectar movimiento horizontal (lectura de izquierda a derecha)
        let horizontalMovement = 0;
        let verticalMovement = 0;
        
        for (let i = 1; i < recentPoints.length; i++) {
            const prev = recentPoints[i - 1];
            const curr = recentPoints[i];
            
            const dx = curr.x - prev.x;
            const dy = curr.y - prev.y;
            
            horizontalMovement += dx;
            verticalMovement += Math.abs(dy);
            
            this.totalMovements++;
            
            // Movimiento de izquierda a derecha (lectura)
            if (dx > 5 && Math.abs(dy) < 30) {
                this.leftToRightMovements++;
            }
            
            // Detectar salto de línea (movimiento grande hacia la izquierda + abajo)
            if (dx < -100 && dy > 20 && dy < this.lineThreshold) {
                this.lineChanges++;
                this.stats.linesRead++;
            }
        }
        
        // Calcular ratio de movimientos de lectura
        const readingRatio = this.totalMovements > 0 
            ? this.leftToRightMovements / this.totalMovements 
            : 0;
        
        // Determinar si está leyendo
        const wasReading = this.isReading;
        this.isReading = readingRatio > 0.4 && this.lineChanges > 0;
        
        // Eventos de inicio/fin de lectura
        if (this.isReading && !wasReading) {
            this.readingStartTime = Date.now();
            this.onReadingStart();
            this.showNotification('📖 Lectura detectada');
        } else if (!this.isReading && wasReading) {
            if (this.readingStartTime) {
                const duration = Date.now() - this.readingStartTime;
                this.stats.totalReadingTime += duration;
            }
            this.onReadingEnd();
            this.showNotification('📕 Fin de lectura');
        }
        
        // Calcular palabras por minuto (estimado)
        if (this.isReading && this.readingStartTime) {
            const readingDuration = (Date.now() - this.readingStartTime) / 1000 / 60; // minutos
            const estimatedWords = this.stats.linesRead * 10; // ~10 palabras por línea
            this.stats.wordsPerMinute = readingDuration > 0 
                ? Math.round(estimatedWords / readingDuration) 
                : 0;
        }
        
        this.onStatsUpdate(this.stats);
    }
    
    updateUI() {
        if (!this.panel) return;
        
        const statusEl = document.getElementById('reading-status');
        const timeEl = document.getElementById('reading-time');
        const linesEl = document.getElementById('lines-read');
        const wpmEl = document.getElementById('words-per-minute');
        const patternEl = document.getElementById('reading-pattern');
        
        if (statusEl) {
            statusEl.textContent = this.isReading ? '✅ Leyendo' : '⏸️ No leyendo';
            statusEl.style.color = this.isReading ? '#4CAF50' : '#FFC107';
        }
        
        if (timeEl && this.readingStartTime) {
            const duration = Math.floor((Date.now() - this.readingStartTime) / 1000);
            timeEl.textContent = duration + 's';
        }
        
        if (linesEl) {
            linesEl.textContent = this.stats.linesRead;
        }
        
        if (wpmEl) {
            wpmEl.textContent = this.stats.wordsPerMinute;
        }
        
        if (patternEl) {
            const ratio = this.totalMovements > 0 
                ? (this.leftToRightMovements / this.totalMovements * 100).toFixed(0) 
                : 0;
            patternEl.textContent = `${ratio}% →`;
        }
    }
    
    showNotification(message) {
        const notification = document.createElement('div');
        notification.style.position = 'fixed';
        notification.style.top = '50%';
        notification.style.left = '50%';
        notification.style.transform = 'translate(-50%, -50%)';
        notification.style.background = 'rgba(0, 0, 0, 0.9)';
        notification.style.color = 'white';
        notification.style.padding = '20px 40px';
        notification.style.borderRadius = '15px';
        notification.style.fontSize = '24px';
        notification.style.fontWeight = 'bold';
        notification.style.zIndex = '99999';
        notification.style.animation = 'fadeInOut 2s ease-in-out';
        notification.textContent = message;
        
        // Añadir animación CSS
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes fadeInOut {
                    0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
                    20% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
                    80% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
                    100% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 2000);
    }
    
    toggle() {
        this.enabled = !this.enabled;
        this.panel.style.display = this.enabled ? 'block' : 'none';
        
        if (!this.enabled) {
            this.reset();
        }
    }
    
    show() {
        this.panel.style.display = 'block';
    }
    
    hide() {
        this.panel.style.display = 'none';
    }
    
    reset() {
        this.gazeHistory = [];
        this.isReading = false;
        this.readingStartTime = null;
        this.currentLine = null;
        this.lineChanges = 0;
        this.leftToRightMovements = 0;
        this.totalMovements = 0;
        this.stats = {
            totalReadingTime: 0,
            linesRead: 0,
            wordsPerMinute: 0,
            lastUpdate: Date.now()
        };
    }
    
    getStats() {
        return {
            ...this.stats,
            isReading: this.isReading,
            currentReadingDuration: this.readingStartTime 
                ? Date.now() - this.readingStartTime 
                : 0
        };
    }
    
    destroy() {
        if (this.panel && this.panel.parentNode) {
            this.panel.parentNode.removeChild(this.panel);
        }
    }
}

// Hacer disponible globalmente
window.ReadingDetector = ReadingDetector;
