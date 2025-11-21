// Sistema de calibración mejorado
class ImprovedCalibration {
    constructor(eyeGesturesInstance) {
        this.eyeGestures = eyeGesturesInstance;
        this.mode = 'standard'; // 'standard' (25 puntos) o 'extended' (49 puntos)
        this.currentPoint = 0;
        this.totalPoints = 25;
        this.pointDuration = 1500; // ms por punto
        this.overlay = null;
        
        // Patrones de calibración
        this.patterns = {
            standard: this.generateGridPattern(5, 5), // 5x5 = 25 puntos
            extended: this.generateGridPattern(7, 7), // 7x7 = 49 puntos
            adaptive: [] // Se genera dinámicamente basándose en errores
        };
    }
    
    generateGridPattern(rows, cols) {
        const points = [];
        const marginX = 0.1; // 10% de margen
        const marginY = 0.1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = marginX + (col / (cols - 1)) * (1 - 2 * marginX);
                const y = marginY + (row / (rows - 1)) * (1 - 2 * marginY);
                points.push([x, y]);
            }
        }
        
        // Optimizar orden: seguir un patrón en espiral o zigzag
        return this.optimizeCalibrationOrder(points);
    }
    
    optimizeCalibrationOrder(points) {
        // Ordenar en patrón zigzag para minimizar distancia entre puntos
        const sorted = [];
        const width = Math.sqrt(points.length);
        
        for (let row = 0; row < width; row++) {
            const rowPoints = [];
            for (let col = 0; col < width; col++) {
                const idx = row * width + col;
                if (idx < points.length) {
                    rowPoints.push(points[idx]);
                }
            }
            
            // Alternar dirección cada fila
            if (row % 2 === 1) {
                rowPoints.reverse();
            }
            
            sorted.push(...rowPoints);
        }
        
        return sorted;
    }
    
    start(mode = 'standard') {
        this.mode = mode;
        this.currentPoint = 0;
        this.totalPoints = this.patterns[mode].length;
        
        // Actualizar matriz de calibración de EyeGestures
        if (this.eyeGestures && this.eyeGestures.calibrator) {
            this.eyeGestures.calibrator.updMatrix(this.patterns[mode]);
            this.eyeGestures.calib_max = this.totalPoints;
        }
        
        this.createOverlay();
        this.showInstructions();
    }
    
    createOverlay() {
        if (this.overlay) {
            this.overlay.remove();
        }
        
        this.overlay = document.createElement('div');
        this.overlay.id = 'improved-calibration-overlay';
        this.overlay.style.position = 'fixed';
        this.overlay.style.top = '0';
        this.overlay.style.left = '0';
        this.overlay.style.width = '100vw';
        this.overlay.style.height = '100vh';
        this.overlay.style.background = 'rgba(0, 0, 0, 0.95)';
        this.overlay.style.zIndex = '10000';
        this.overlay.style.display = 'flex';
        this.overlay.style.justifyContent = 'center';
        this.overlay.style.alignItems = 'center';
        
        // Indicador de progreso
        const progress = document.createElement('div');
        progress.id = 'calibration-progress';
        progress.style.position = 'fixed';
        progress.style.top = '20px';
        progress.style.left = '50%';
        progress.style.transform = 'translateX(-50%)';
        progress.style.background = 'rgba(255, 255, 255, 0.9)';
        progress.style.color = 'black';
        progress.style.padding = '15px 30px';
        progress.style.borderRadius = '25px';
        progress.style.fontWeight = 'bold';
        progress.style.fontSize = '18px';
        progress.style.boxShadow = '0 4px 20px rgba(0,0,0,0.5)';
        
        this.overlay.appendChild(progress);
        document.body.appendChild(this.overlay);
        
        this.updateProgress();
    }
    
    updateProgress() {
        const progress = document.getElementById('calibration-progress');
        if (progress) {
            const percent = Math.floor((this.currentPoint / this.totalPoints) * 100);
            progress.textContent = `🎯 Calibración: ${this.currentPoint}/${this.totalPoints} (${percent}%)`;
            
            // Barra de progreso visual
            progress.style.background = `linear-gradient(to right, 
                #5e17eb ${percent}%, 
                rgba(255, 255, 255, 0.9) ${percent}%)`;
        }
    }
    
    showInstructions() {
        const instructions = document.createElement('div');
        instructions.style.position = 'fixed';
        instructions.style.top = '50%';
        instructions.style.left = '50%';
        instructions.style.transform = 'translate(-50%, -50%)';
        instructions.style.background = 'rgba(255, 255, 255, 0.95)';
        instructions.style.padding = '40px';
        instructions.style.borderRadius = '20px';
        instructions.style.textAlign = 'center';
        instructions.style.maxWidth = '600px';
        instructions.style.zIndex = '10001';
        instructions.style.boxShadow = '0 10px 50px rgba(0,0,0,0.5)';
        
        const modeText = {
            'standard': '25 puntos - Calibración estándar (recomendado)',
            'extended': '49 puntos - Calibración de alta precisión'
        };
        
        instructions.innerHTML = `
            <h2 style="margin: 0 0 20px 0; color: #5e17eb;">
                🎯 Calibración Mejorada
            </h2>
            <p style="font-size: 18px; margin-bottom: 20px;">
                Modo: <strong>${modeText[this.mode]}</strong>
            </p>
            <div style="text-align: left; margin: 20px 0; background: #f5f5f5; padding: 20px; border-radius: 10px;">
                <p style="margin: 10px 0;">
                    <span style="color: #ff5757; font-size: 24px;">🔴</span>
                    <strong>Círculo rojo</strong> = Objetivo a mirar
                </p>
                <p style="margin: 10px 0;">
                    <span style="color: #5e17eb; font-size: 24px;">🔵</span>
                    <strong>Círculo azul</strong> = Tu mirada detectada
                </p>
            </div>
            <p style="margin: 20px 0;">
                <strong>Instrucciones:</strong><br>
                1️⃣ Mantén la cabeza quieta<br>
                2️⃣ Mira fijamente cada círculo rojo<br>
                3️⃣ El sistema avanza automáticamente<br>
                4️⃣ Intenta no mover los ojos hasta que cambie
            </p>
            <button id="start-calibration-btn" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 40px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 50px;
                cursor: pointer;
                margin-top: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                transition: transform 0.3s;
            " onmouseover="this.style.transform='scale(1.1)'" 
               onmouseout="this.style.transform='scale(1)'">
                ▶️ Comenzar Calibración
            </button>
        `;
        
        this.overlay.appendChild(instructions);
        
        document.getElementById('start-calibration-btn').addEventListener('click', () => {
            instructions.remove();
            if (this.eyeGestures) {
                this.eyeGestures.__run();
            }
        });
    }
    
    onPointComplete() {
        this.currentPoint++;
        this.updateProgress();
        
        // Feedback visual
        this.showPointCompleteFeedback();
        
        if (this.currentPoint >= this.totalPoints) {
            this.onCalibrationComplete();
        }
    }
    
    showPointCompleteFeedback() {
        const feedback = document.createElement('div');
        feedback.style.position = 'fixed';
        feedback.style.top = '100px';
        feedback.style.left = '50%';
        feedback.style.transform = 'translateX(-50%)';
        feedback.style.background = 'rgba(76, 175, 80, 0.9)';
        feedback.style.color = 'white';
        feedback.style.padding = '10px 20px';
        feedback.style.borderRadius = '10px';
        feedback.style.fontWeight = 'bold';
        feedback.style.zIndex = '10002';
        feedback.style.animation = 'fadeOut 1s ease-out';
        feedback.textContent = '✅ Punto capturado';
        
        // Añadir animación
        if (!document.getElementById('calibration-feedback-style')) {
            const style = document.createElement('style');
            style.id = 'calibration-feedback-style';
            style.textContent = `
                @keyframes fadeOut {
                    0% { opacity: 1; transform: translateX(-50%) translateY(0); }
                    100% { opacity: 0; transform: translateX(-50%) translateY(-20px); }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(feedback);
        
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.parentNode.removeChild(feedback);
            }
        }, 1000);
    }
    
    onCalibrationComplete() {
        // Mostrar overlay de finalización
        const complete = document.createElement('div');
        complete.style.position = 'fixed';
        complete.style.top = '50%';
        complete.style.left = '50%';
        complete.style.transform = 'translate(-50%, -50%)';
        complete.style.background = 'rgba(76, 175, 80, 0.95)';
        complete.style.color = 'white';
        complete.style.padding = '40px';
        complete.style.borderRadius = '20px';
        complete.style.textAlign = 'center';
        complete.style.zIndex = '10003';
        complete.style.fontSize = '24px';
        complete.style.fontWeight = 'bold';
        complete.style.boxShadow = '0 10px 50px rgba(0,0,0,0.5)';
        
        complete.innerHTML = `
            <div style="font-size: 60px; margin-bottom: 20px;">✅</div>
            <div>¡Calibración Completada!</div>
            <div style="font-size: 16px; margin-top: 20px; font-weight: normal;">
                Iniciando juego...
            </div>
        `;
        
        this.overlay.appendChild(complete);
        
        // Cerrar overlay después de 2 segundos
        setTimeout(() => {
            if (this.overlay && this.overlay.parentNode) {
                this.overlay.parentNode.removeChild(this.overlay);
                this.overlay = null;
            }
        }, 2000);
    }
    
    cancel() {
        if (this.overlay && this.overlay.parentNode) {
            this.overlay.parentNode.removeChild(this.overlay);
            this.overlay = null;
        }
    }
}

// Hacer disponible globalmente
window.ImprovedCalibration = ImprovedCalibration;
