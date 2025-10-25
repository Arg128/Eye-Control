/**
 * Global Gaze Trail Integration
 * Script que añade automáticamente el rastro de mirada y heatmap a cualquier página
 * Solo se necesita incluir este script y gazeTrail.js
 */

(function() {
    'use strict';
    
    console.log('🎯 Inicializando Global Gaze Trail...');
    
    // Configuración global
    const GLOBAL_CONFIG = {
        trailColor: 'rgba(69, 123, 157, 0.7)', // #457b9d de la paleta
        maxPoints: 50,
        pointSize: 18,
        fadeSpeed: 0.96,
        enabledByDefault: true,
        showPanel: true,
        panelPosition: 'bottom-right' // 'top-left', 'top-right', 'bottom-left', 'bottom-right'
    };
    
    let globalGazeTrail = null;
    let eyeGesturesInstance = null;
    
    // Esperar a que el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    function init() {
        // Verificar que GazeTrail esté disponible
        if (typeof GazeTrail === 'undefined') {
            console.warn('⚠️ GazeTrail no está disponible. Asegúrate de incluir gazeTrail.js');
            return;
        }
        
        // Inicializar GazeTrail global
        globalGazeTrail = new GazeTrail({
            enabled: GLOBAL_CONFIG.enabledByDefault,
            maxPoints: GLOBAL_CONFIG.maxPoints,
            trailColor: GLOBAL_CONFIG.trailColor,
            pointSize: GLOBAL_CONFIG.pointSize,
            fadeSpeed: GLOBAL_CONFIG.fadeSpeed,
            showHeatmap: false
        });
        
        // Crear panel de control si está habilitado
        if (GLOBAL_CONFIG.showPanel) {
            createGlobalControlPanel();
        }
        
        // Intentar conectar con EyeGestures si está disponible
        connectToEyeGestures();
        
        // Exponer globalmente
        window.globalGazeTrail = globalGazeTrail;
        
        console.log('✅ Global Gaze Trail inicializado');
    }
    
    function createGlobalControlPanel() {
        const panel = document.createElement('div');
        panel.id = 'global-gaze-controls';
        panel.style.cssText = getControlPanelStyles();
        
        panel.innerHTML = `
            <div class="panel-header">
                <h4 style="margin: 0; font-size: 14px; color: #f1faee;">👁️ Rastro de Mirada</h4>
                <button id="toggle-panel-btn" style="background: none; border: none; color: #f1faee; cursor: pointer; font-size: 16px;">−</button>
            </div>
            <div id="panel-content" class="panel-content">
                <div style="margin: 10px 0;">
                    <button id="global-toggle-trail" class="gaze-btn gaze-btn-primary">
                        ${GLOBAL_CONFIG.enabledByDefault ? '🟢 Rastro: ON' : '⚪ Rastro: OFF'}
                    </button>
                </div>
                <div style="margin: 10px 0;">
                    <button id="global-toggle-heatmap" class="gaze-btn gaze-btn-secondary" ${!GLOBAL_CONFIG.enabledByDefault ? 'disabled' : ''}>
                        🔥 Heatmap: OFF
                    </button>
                </div>
                <div style="margin: 10px 0;">
                    <button id="global-clear-trail" class="gaze-btn gaze-btn-danger">
                        🗑️ Limpiar
                    </button>
                </div>
                <div style="margin: 10px 0; padding-top: 10px; border-top: 1px solid rgba(168, 218, 220, 0.3);">
                    <label style="display: block; font-size: 12px; margin-bottom: 5px; color: #a8dadc;">Tamaño del punto:</label>
                    <input type="range" id="global-point-size" min="10" max="30" value="${GLOBAL_CONFIG.pointSize}" style="width: 100%;">
                    <small id="point-size-value" style="color: #a8dadc; font-size: 11px;">${GLOBAL_CONFIG.pointSize}px</small>
                </div>
            </div>
            <style>
                #global-gaze-controls {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                .panel-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                    padding-bottom: 8px;
                    border-bottom: 2px solid rgba(168, 218, 220, 0.5);
                }
                .panel-content {
                    transition: all 0.3s;
                }
                .panel-content.collapsed {
                    display: none;
                }
                .gaze-btn {
                    width: 100%;
                    padding: 10px;
                    border: none;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.3s;
                    color: #f1faee;
                }
                .gaze-btn:hover:not(:disabled) {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
                }
                .gaze-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                .gaze-btn-primary {
                    background: linear-gradient(135deg, #457b9d, #1d3557);
                }
                .gaze-btn-secondary {
                    background: linear-gradient(135deg, #e63946, #c1121f);
                }
                .gaze-btn-danger {
                    background: linear-gradient(135deg, #78909c, #546e7a);
                }
                .gaze-btn.active {
                    box-shadow: 0 0 15px rgba(168, 218, 220, 0.8);
                    border: 2px solid #a8dadc;
                }
            </style>
        `;
        
        document.body.appendChild(panel);
        
        // Event listeners
        document.getElementById('global-toggle-trail').addEventListener('click', toggleTrail);
        document.getElementById('global-toggle-heatmap').addEventListener('click', toggleHeatmap);
        document.getElementById('global-clear-trail').addEventListener('click', clearTrail);
        document.getElementById('global-point-size').addEventListener('input', updatePointSize);
        document.getElementById('toggle-panel-btn').addEventListener('click', togglePanelCollapse);
    }
    
    function getControlPanelStyles() {
        const positions = {
            'top-left': 'top: 20px; left: 20px;',
            'top-right': 'top: 20px; right: 20px;',
            'bottom-left': 'bottom: 20px; left: 20px;',
            'bottom-right': 'bottom: 20px; right: 20px;'
        };
        
        const baseStyle = `
            position: fixed;
            background: linear-gradient(135deg, rgba(29, 53, 87, 0.95), rgba(69, 123, 157, 0.95));
            color: #f1faee;
            padding: 15px;
            border-radius: 12px;
            z-index: 999999;
            min-width: 200px;
            max-width: 250px;
            box-shadow: 0 8px 32px rgba(69, 123, 157, 0.4);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(168, 218, 220, 0.3);
        `;
        
        return baseStyle + (positions[GLOBAL_CONFIG.panelPosition] || positions['bottom-right']);
    }
    
    function toggleTrail() {
        if (!globalGazeTrail) return;
        
        globalGazeTrail.toggle();
        const btn = document.getElementById('global-toggle-trail');
        const heatmapBtn = document.getElementById('global-toggle-heatmap');
        
        if (globalGazeTrail.enabled) {
            btn.textContent = '🟢 Rastro: ON';
            btn.classList.add('active');
            heatmapBtn.disabled = false;
        } else {
            btn.textContent = '⚪ Rastro: OFF';
            btn.classList.remove('active');
            heatmapBtn.disabled = true;
        }
    }
    
    function toggleHeatmap() {
        if (!globalGazeTrail) return;
        
        globalGazeTrail.toggleHeatmap();
        const btn = document.getElementById('global-toggle-heatmap');
        
        if (globalGazeTrail.showHeatmap) {
            btn.textContent = '🔥 Heatmap: ON';
            btn.classList.add('active');
        } else {
            btn.textContent = '🔥 Heatmap: OFF';
            btn.classList.remove('active');
        }
    }
    
    function clearTrail() {
        if (!globalGazeTrail) return;
        globalGazeTrail.clear();
    }
    
    function updatePointSize(e) {
        const value = parseInt(e.target.value);
        document.getElementById('point-size-value').textContent = value + 'px';
        
        if (globalGazeTrail) {
            globalGazeTrail.pointSize = value;
        }
    }
    
    function togglePanelCollapse() {
        const content = document.getElementById('panel-content');
        const btn = document.getElementById('toggle-panel-btn');
        
        content.classList.toggle('collapsed');
        btn.textContent = content.classList.contains('collapsed') ? '+' : '−';
    }
    
    function connectToEyeGestures() {
        // Intentar conectar cada 500ms durante 5 segundos
        let attempts = 0;
        const maxAttempts = 10;
        
        const checkInterval = setInterval(() => {
            attempts++;
            
            // Buscar instancia de EyeGestures en window
            if (window.eyeGestures || window.EyeGestures) {
                eyeGesturesInstance = window.eyeGestures || window.EyeGestures;
                console.log('✅ Conectado a EyeGestures');
                
                // Interceptar callback de gaze
                const originalCallback = eyeGesturesInstance.callback;
                eyeGesturesInstance.callback = function(data) {
                    if (originalCallback) {
                        originalCallback.call(this, data);
                    }
                    
                    // Añadir puntos al trail
                    if (data.x !== undefined && data.y !== undefined && globalGazeTrail) {
                        globalGazeTrail.addPoint(data.x, data.y, data.confidence || 1.0);
                    }
                };
                
                clearInterval(checkInterval);
            }
            
            if (attempts >= maxAttempts) {
                console.log('ℹ️ EyeGestures no detectado (modo standalone)');
                clearInterval(checkInterval);
            }
        }, 500);
    }
    
    // Exponer API global
    window.GlobalGazeTrail = {
        enable: function() {
            if (globalGazeTrail) globalGazeTrail.enabled = true;
        },
        disable: function() {
            if (globalGazeTrail) globalGazeTrail.enabled = false;
        },
        clear: function() {
            if (globalGazeTrail) globalGazeTrail.clear();
        },
        toggleHeatmap: function() {
            if (globalGazeTrail) globalGazeTrail.toggleHeatmap();
        },
        setColor: function(color) {
            if (globalGazeTrail) globalGazeTrail.setColor(color);
        },
        addPoint: function(x, y, intensity) {
            if (globalGazeTrail) globalGazeTrail.addPoint(x, y, intensity);
        }
    };
    
})();
