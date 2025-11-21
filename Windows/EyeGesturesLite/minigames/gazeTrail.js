// Sistema de rastro visual de mirada (Gaze Trail)
class GazeTrail {
    constructor(options = {}) {
        this.enabled = options.enabled !== undefined ? options.enabled : true;
        this.maxPoints = options.maxPoints || 50;
        this.trailColor = options.trailColor || 'rgba(69, 123, 157, 0.7)'; // #457b9d de la paleta
        this.pointSize = options.pointSize || 18; // Ligeramente más grande
        this.fadeSpeed = options.fadeSpeed || 0.96; // Fade más suave
        this.showHeatmap = options.showHeatmap !== undefined ? options.showHeatmap : false;
        
        this.points = [];
        this.heatmapData = [];
        
        this.createCanvas();
        this.startAnimation();
    }
    
    createCanvas() {
        // Canvas para el rastro
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'gaze-trail-canvas';
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.pointerEvents = 'none';
        this.canvas.style.zIndex = '9998';
        this.canvas.style.display = this.enabled ? 'block' : 'none';
        document.body.appendChild(this.canvas);
        
        this.ctx = this.canvas.getContext('2d');
        
        // Ajustar tamaño en resize
        window.addEventListener('resize', () => {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        });
    }
    
    addPoint(x, y, intensity = 1.0) {
        if (!this.enabled) return;
        
        const point = {
            x: x,
            y: y,
            intensity: intensity,
            timestamp: Date.now(),
            alpha: 1.0
        };
        
        this.points.push(point);
        
        // Limitar número de puntos
        if (this.points.length > this.maxPoints) {
            this.points.shift();
        }
        
        // Añadir a heatmap
        if (this.showHeatmap) {
            this.heatmapData.push({x, y, value: intensity});
            if (this.heatmapData.length > 500) {
                this.heatmapData.shift();
            }
        }
    }
    
    startAnimation() {
        const animate = () => {
            this.draw();
            requestAnimationFrame(animate);
        };
        animate();
    }
    
    draw() {
        if (!this.enabled) return;
        
        // Limpiar canvas con fade
        this.ctx.fillStyle = 'rgba(255, 255, 255, ' + (1 - this.fadeSpeed) + ')';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Dibujar puntos del rastro
        for (let i = 0; i < this.points.length; i++) {
            const point = this.points[i];
            const age = Date.now() - point.timestamp;
            const maxAge = 3000; // 3 segundos
            
            // Calcular alpha basado en edad
            point.alpha = Math.max(0, 1 - (age / maxAge));
            
            if (point.alpha <= 0) {
                this.points.splice(i, 1);
                i--;
                continue;
            }
            
            // Dibujar punto con gradiente moderno (paleta #457b9d -> #a8dadc)
            const gradient = this.ctx.createRadialGradient(
                point.x, point.y, 0,
                point.x, point.y, this.pointSize
            );
            
            const color = this.hexToRgb(this.trailColor);
            // Gradiente desde azul medio (#457b9d) hacia azul claro (#a8dadc)
            gradient.addColorStop(0, `rgba(${color.r}, ${color.g}, ${color.b}, ${point.alpha * 0.9})`);
            gradient.addColorStop(0.4, `rgba(${Math.min(color.r + 99, 255)}, ${Math.min(color.g + 95, 255)}, ${Math.min(color.b + 63, 255)}, ${point.alpha * 0.6})`);
            gradient.addColorStop(1, `rgba(${color.r}, ${color.g}, ${color.b}, 0)`);
            
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(point.x, point.y, this.pointSize, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Conectar con línea al punto anterior (colores de la paleta)
            if (i > 0) {
                const prevPoint = this.points[i - 1];
                const avgAlpha = (point.alpha + prevPoint.alpha) / 2;
                // Usar color #a8dadc (azul claro) para las líneas
                this.ctx.strokeStyle = `rgba(168, 218, 220, ${avgAlpha * 0.5})`;
                this.ctx.lineWidth = 3;
                this.ctx.lineCap = 'round';
                this.ctx.beginPath();
                this.ctx.moveTo(prevPoint.x, prevPoint.y);
                this.ctx.lineTo(point.x, point.y);
                this.ctx.stroke();
            }
        }
        
        // Dibujar heatmap si está habilitado
        if (this.showHeatmap) {
            this.drawHeatmap();
        }
    }
    
    drawHeatmap() {
        const gridSize = 40;
        const grid = {};
        
        // Agrupar puntos en grid
        for (const point of this.heatmapData) {
            const gridX = Math.floor(point.x / gridSize);
            const gridY = Math.floor(point.y / gridSize);
            const key = `${gridX},${gridY}`;
            
            if (!grid[key]) {
                grid[key] = { x: gridX * gridSize, y: gridY * gridSize, count: 0 };
            }
            grid[key].count += point.value;
        }
        
        // Encontrar máximo
        let maxCount = 0;
        for (const key in grid) {
            maxCount = Math.max(maxCount, grid[key].count);
        }
        
        // Dibujar celdas del heatmap con colores de la paleta
        for (const key in grid) {
            const cell = grid[key];
            const intensity = cell.count / maxCount;
            
            // Paleta: #a8dadc (frío) -> #457b9d (medio) -> #e63946 (caliente)
            let r, g, b;
            if (intensity < 0.5) {
                // De azul claro (#a8dadc) a azul medio (#457b9d)
                const t = intensity * 2;
                r = Math.floor(168 + (69 - 168) * t);    // 168 -> 69
                g = Math.floor(218 + (123 - 218) * t);   // 218 -> 123
                b = Math.floor(220 + (157 - 220) * t);   // 220 -> 157
            } else {
                // De azul medio (#457b9d) a rojo (#e63946)
                const t = (intensity - 0.5) * 2;
                r = Math.floor(69 + (230 - 69) * t);     // 69 -> 230
                g = Math.floor(123 + (57 - 123) * t);    // 123 -> 57
                b = Math.floor(157 + (70 - 157) * t);    // 157 -> 70
            }
            
            this.ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${intensity * 0.4})`;
            this.ctx.fillRect(cell.x, cell.y, gridSize, gridSize);
        }
    }
    
    hexToRgb(hex) {
        // Si es rgba, extraer rgb
        if (hex.startsWith('rgba')) {
            const match = hex.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
            if (match) {
                return {
                    r: parseInt(match[1]),
                    g: parseInt(match[2]),
                    b: parseInt(match[3])
                };
            }
        }
        
        // Por defecto - #457b9d (azul medio de la paleta)
        return { r: 69, g: 123, b: 157 };
    }
    
    toggle() {
        this.enabled = !this.enabled;
        this.canvas.style.display = this.enabled ? 'block' : 'none';
        if (!this.enabled) {
            this.clear();
        }
    }
    
    clear() {
        this.points = [];
        this.heatmapData = [];
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    toggleHeatmap() {
        this.showHeatmap = !this.showHeatmap;
        if (!this.showHeatmap) {
            this.heatmapData = [];
        }
    }
    
    setColor(color) {
        this.trailColor = color;
    }
    
    destroy() {
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
    }
}

// Hacer disponible globalmente
window.GazeTrail = GazeTrail;
