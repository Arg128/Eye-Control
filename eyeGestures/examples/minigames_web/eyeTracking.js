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
        const indicator = document.getElementById('statusIndicator');
        const text = document.getElementById('statusText');
        
        indicator.className = 'status-indicator';
        
        switch (status) {
            case 'connected':
                indicator.classList.add('connected');
                text.textContent = 'Conectado';
                break;
            case 'connecting':
                text.textContent = 'Conectando...';
                break;
            case 'disconnected':
                indicator.classList.add('disconnected');
                text.textContent = 'Desconectado (usando ratón)';
                break;
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
            
            // Update UI elements
            document.getElementById('gazeX').textContent = Math.round(this.gazeX);
            document.getElementById('gazeY').textContent = Math.round(this.gazeY);
            document.getElementById('fixation').textContent = this.fixation.toFixed(2);
            
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
