/**
 * TimeTracker - Sistema de detección de tiempo y atención del usuario
 * Detecta cuánto tiempo está en la página y cuando mira fuera de ella
 */

class TimeTracker {
    constructor() {
        this.startTime = Date.now();
        this.timeOnPage = 0;
        this.timeLooking = 0;
        this.timeAway = 0;
        this.isLooking = true;
        this.lastUpdate = Date.now();
        this.lastGazeTime = Date.now();
        this.gazeTimeout = 2000; // 2 segundos sin movimiento de ojos = usuario no está mirando
        this.hasRecentGaze = false;
        
        // Elementos del DOM
        this.timeOnPageEl = document.getElementById('time-on-page');
        this.attentionStatusEl = document.getElementById('attention-status');
        this.timeLookingEl = document.getElementById('time-looking');
        this.timeAwayEl = document.getElementById('time-away');
        this.attentionPercentEl = document.getElementById('attention-percent');
        
        // Iniciar actualizaciones
        this.startTracking();
        
        // Eventos de visibilidad de página
        this.setupVisibilityTracking();
        
        // Eventos de mouse/teclado como backup
        this.setupInteractionTracking();
    }
    
    startTracking() {
        // Actualizar cada 100ms
        this.trackingInterval = setInterval(() => {
            this.update();
        }, 100);
    }
    
    update() {
        const now = Date.now();
        const delta = (now - this.lastUpdate) / 1000;
        
        this.timeOnPage += delta;
        
        // Verificar si el usuario está mirando (ha habido actividad de ojos reciente)
        const timeSinceLastGaze = now - this.lastGazeTime;
        const wasLooking = this.isLooking;
        this.isLooking = timeSinceLastGaze < this.gazeTimeout && !document.hidden;
        
        if (this.isLooking) {
            this.timeLooking += delta;
        } else {
            this.timeAway += delta;
        }
        
        // Disparar evento si cambió el estado
        if (wasLooking !== this.isLooking) {
            this.onStatusChange(this.isLooking);
        }
        
        this.lastUpdate = now;
        this.updateUI();
    }
    
    onStatusChange(isLooking) {
        // Evento personalizado que otros pueden escuchar
        const event = new CustomEvent('attentionchange', {
            detail: {
                isLooking: isLooking,
                timeLooking: this.timeLooking,
                timeAway: this.timeAway,
                attentionPercent: this.getAttentionPercent()
            }
        });
        document.dispatchEvent(event);
    }
    
    // Llamar esto cuando se detecte movimiento de ojos
    onGazeDetected(x, y) {
        this.lastGazeTime = Date.now();
        this.hasRecentGaze = true;
    }
    
    getAttentionPercent() {
        if (this.timeOnPage === 0) return 100;
        return Math.round((this.timeLooking / this.timeOnPage) * 100);
    }
    
    formatTime(seconds) {
        if (seconds < 60) {
            return Math.floor(seconds) + 's';
        } else if (seconds < 3600) {
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins}m ${secs}s`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const mins = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${mins}m`;
        }
    }
    
    updateUI() {
        if (!this.timeOnPageEl) return;
        
        this.timeOnPageEl.textContent = this.formatTime(this.timeOnPage);
        this.timeLookingEl.textContent = this.formatTime(this.timeLooking);
        this.timeAwayEl.textContent = this.formatTime(this.timeAway);
        this.attentionPercentEl.textContent = this.getAttentionPercent() + '%';
        
        // Actualizar estado visual
        if (this.isLooking) {
            this.attentionStatusEl.textContent = 'Mirando 👀';
            this.attentionStatusEl.style.color = '#4CAF50';
        } else {
            this.attentionStatusEl.textContent = 'Fuera 😴';
            this.attentionStatusEl.style.color = '#ff5757';
        }
        
        // Color del porcentaje según atención
        const percent = this.getAttentionPercent();
        if (percent >= 80) {
            this.attentionPercentEl.style.color = '#4CAF50';
        } else if (percent >= 50) {
            this.attentionPercentEl.style.color = '#FFC107';
        } else {
            this.attentionPercentEl.style.color = '#ff5757';
        }
    }
    
    setupVisibilityTracking() {
        // Detectar cuando la pestaña está oculta
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.isLooking = false;
            }
        });
    }
    
    setupInteractionTracking() {
        // Backup: usar mouse/teclado como indicador de presencia
        let interactionTimeout;
        
        const onInteraction = () => {
            this.lastGazeTime = Date.now();
            clearTimeout(interactionTimeout);
            
            // Si no hay movimiento por 5 segundos, asumir que se fue
            interactionTimeout = setTimeout(() => {
                // No hacer nada, el sistema de gaze ya maneja esto
            }, 5000);
        };
        
        document.addEventListener('mousemove', onInteraction);
        document.addEventListener('keypress', onInteraction);
        document.addEventListener('click', onInteraction);
    }
    
    // API pública
    getStats() {
        return {
            timeOnPage: this.timeOnPage,
            timeLooking: this.timeLooking,
            timeAway: this.timeAway,
            isLooking: this.isLooking,
            attentionPercent: this.getAttentionPercent()
        };
    }
    
    reset() {
        this.startTime = Date.now();
        this.timeOnPage = 0;
        this.timeLooking = 0;
        this.timeAway = 0;
        this.isLooking = true;
        this.lastUpdate = Date.now();
        this.updateUI();
    }
    
    destroy() {
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
        }
    }
}

// Exportar para uso global
window.TimeTracker = TimeTracker;
