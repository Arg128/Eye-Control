// Filtro de Kalman para suavizar y predecir posiciones de mirada
class GazeFilter {
    constructor(options = {}) {
        // Parámetros del filtro de Kalman
        this.processNoise = options.processNoise || 0.01;
        this.measurementNoise = options.measurementNoise || 10;
        this.estimationError = options.estimationError || 1;
        
        // Estado del filtro (x, y, vx, vy)
        this.state = {
            x: 0,
            y: 0,
            vx: 0,
            vy: 0
        };
        
        // Matriz de covarianza
        this.P = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ];
        
        // Filtro adicional: Media móvil exponencial
        this.emaAlpha = options.emaAlpha || 0.3;
        this.emaX = null;
        this.emaY = null;
        
        // Detección de outliers
        this.maxJumpDistance = options.maxJumpDistance || 200;
        this.lastValidPoint = null;
        
        // Buffer circular para estadísticas
        this.recentPoints = [];
        this.bufferSize = 10;
        
        // Contador de frames
        this.frameCount = 0;
    }
    
    filter(x, y) {
        this.frameCount++;
        
        // Inicializar EMA en el primer punto
        if (this.emaX === null) {
            this.emaX = x;
            this.emaY = y;
            this.state.x = x;
            this.state.y = y;
            this.lastValidPoint = { x, y };
            return { x, y, confidence: 1.0 };
        }
        
        // Detectar outliers (saltos anormales)
        const distance = Math.sqrt(
            Math.pow(x - this.lastValidPoint.x, 2) + 
            Math.pow(y - this.lastValidPoint.y, 2)
        );
        
        let isOutlier = distance > this.maxJumpDistance;
        let confidence = 1.0;
        
        if (isOutlier) {
            // Si es outlier, usar predicción en lugar de medición
            confidence = 0.3;
            console.log('Outlier detectado, usando predicción');
        } else {
            this.lastValidPoint = { x, y };
        }
        
        // Aplicar filtro de Kalman
        const filtered = this.kalmanFilter(x, y, isOutlier);
        
        // Aplicar EMA adicional
        this.emaX = this.emaAlpha * filtered.x + (1 - this.emaAlpha) * this.emaX;
        this.emaY = this.emaAlpha * filtered.y + (1 - this.emaAlpha) * this.emaY;
        
        // Añadir a buffer
        this.recentPoints.push({ x: this.emaX, y: this.emaY, timestamp: Date.now() });
        if (this.recentPoints.length > this.bufferSize) {
            this.recentPoints.shift();
        }
        
        return {
            x: Math.round(this.emaX),
            y: Math.round(this.emaY),
            rawX: x,
            rawY: y,
            velocity: {
                vx: this.state.vx,
                vy: this.state.vy
            },
            confidence: confidence,
            isOutlier: isOutlier
        };
    }
    
    kalmanFilter(measX, measY, skipMeasurement) {
        // Predicción
        const dt = 1.0 / 30.0; // Asumiendo ~30 FPS
        
        // Estado predicho
        const predX = this.state.x + this.state.vx * dt;
        const predY = this.state.y + this.state.vy * dt;
        const predVx = this.state.vx;
        const predVy = this.state.vy;
        
        // Matriz de transición
        const F = [
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ];
        
        // Predicción de covarianza: P = F*P*F' + Q
        this.P = this.matrixAdd(
            this.matrixMultiply(this.matrixMultiply(F, this.P), this.transpose(F)),
            this.identityMatrix(4, this.processNoise)
        );
        
        // Actualización (si no es outlier)
        if (!skipMeasurement) {
            // Innovación (diferencia entre medición y predicción)
            const y_innov_x = measX - predX;
            const y_innov_y = measY - predY;
            
            // Ganancia de Kalman
            const S = this.P[0][0] + this.measurementNoise;
            const K_x = this.P[0][0] / S;
            const K_y = this.P[1][1] / (this.P[1][1] + this.measurementNoise);
            
            // Estado actualizado
            this.state.x = predX + K_x * y_innov_x;
            this.state.y = predY + K_y * y_innov_y;
            this.state.vx = predVx + (K_x * y_innov_x) / dt;
            this.state.vy = predVy + (K_y * y_innov_y) / dt;
            
            // Actualizar covarianza: P = (I - K*H)*P
            const K = [
                [K_x, 0, 0, 0],
                [0, K_y, 0, 0],
                [0, 0, K_x / dt, 0],
                [0, 0, 0, K_y / dt]
            ];
            
            const I = this.identityMatrix(4, 1);
            const H = [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ];
            
            this.P = this.matrixMultiply(
                this.matrixSubtract(I, this.matrixMultiply(K, H)),
                this.P
            );
        } else {
            // Usar solo predicción
            this.state.x = predX;
            this.state.y = predY;
            this.state.vx = predVx;
            this.state.vy = predVy;
        }
        
        return { x: this.state.x, y: this.state.y };
    }
    
    // Utilidades de matrices
    matrixMultiply(A, B) {
        const result = [];
        for (let i = 0; i < A.length; i++) {
            result[i] = [];
            for (let j = 0; j < B[0].length; j++) {
                let sum = 0;
                for (let k = 0; k < A[0].length; k++) {
                    sum += A[i][k] * B[k][j];
                }
                result[i][j] = sum;
            }
        }
        return result;
    }
    
    matrixAdd(A, B) {
        const result = [];
        for (let i = 0; i < A.length; i++) {
            result[i] = [];
            for (let j = 0; j < A[0].length; j++) {
                result[i][j] = A[i][j] + B[i][j];
            }
        }
        return result;
    }
    
    matrixSubtract(A, B) {
        const result = [];
        for (let i = 0; i < A.length; i++) {
            result[i] = [];
            for (let j = 0; j < A[0].length; j++) {
                result[i][j] = A[i][j] - B[i][j];
            }
        }
        return result;
    }
    
    transpose(A) {
        const result = [];
        for (let j = 0; j < A[0].length; j++) {
            result[j] = [];
            for (let i = 0; i < A.length; i++) {
                result[j][i] = A[i][j];
            }
        }
        return result;
    }
    
    identityMatrix(size, scale = 1) {
        const result = [];
        for (let i = 0; i < size; i++) {
            result[i] = [];
            for (let j = 0; j < size; j++) {
                result[i][j] = (i === j) ? scale : 0;
            }
        }
        return result;
    }
    
    getVelocity() {
        return Math.sqrt(this.state.vx * this.state.vx + this.state.vy * this.state.vy);
    }
    
    getStats() {
        if (this.recentPoints.length < 2) {
            return null;
        }
        
        // Calcular estadísticas de los puntos recientes
        let totalDist = 0;
        let maxDist = 0;
        
        for (let i = 1; i < this.recentPoints.length; i++) {
            const p1 = this.recentPoints[i - 1];
            const p2 = this.recentPoints[i];
            const dist = Math.sqrt(
                Math.pow(p2.x - p1.x, 2) + 
                Math.pow(p2.y - p1.y, 2)
            );
            totalDist += dist;
            maxDist = Math.max(maxDist, dist);
        }
        
        const avgDist = totalDist / (this.recentPoints.length - 1);
        
        return {
            averageMovement: avgDist,
            maxMovement: maxDist,
            velocity: this.getVelocity(),
            stability: maxDist < 20 ? 'Alta' : maxDist < 50 ? 'Media' : 'Baja'
        };
    }
    
    reset() {
        this.state = { x: 0, y: 0, vx: 0, vy: 0 };
        this.P = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ];
        this.emaX = null;
        this.emaY = null;
        this.lastValidPoint = null;
        this.recentPoints = [];
        this.frameCount = 0;
    }
}

// Hacer disponible globalmente
window.GazeFilter = GazeFilter;
