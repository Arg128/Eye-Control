/**
 * Main.js - Controlador principal de la aplicación de minijuegos
 */

let eyeGestures;
let timeTracker;
let currentGame = null;
let isCalibrated = false;

// Sistemas mejorados
let gazeTrail = null;
let readingDetector = null;
let gazeFilter = null;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    init();
});

function init() {
    console.log('Inicializando EyeGestures Minigames...');
    
    // Inicializar TimeTracker
    timeTracker = new TimeTracker();
    
    // Inicializar sistemas mejorados
    gazeTrail = new GazeTrail({
        enabled: true, // Activado por defecto para mostrar el rastro
        maxPoints: 50,
        trailColor: 'rgba(69, 123, 157, 0.7)', // Color de la nueva paleta (#457b9d)
        showHeatmap: false
    });
    
    readingDetector = new ReadingDetector({
        enabled: false, // Desactivado por defecto
        onReadingStart: () => {
            console.log('📖 Lectura detectada');
        },
        onReadingEnd: () => {
            console.log('📕 Fin de lectura');
        },
        onStatsUpdate: (stats) => {
            // Actualizar UI si es necesario
        }
    });
    
    gazeFilter = new GazeFilter({
        processNoise: 0.01,
        measurementNoise: 5, // Más bajo = más suave
        maxJumpDistance: 300
    });
    
    // Crear controles de funciones avanzadas
    createAdvancedControls();
    
    // Escuchar eventos de cambio de atención
    document.addEventListener('attentionchange', (e) => {
        console.log('Estado de atención:', e.detail);
        
        // Si el usuario se va durante un juego, pausar o mostrar mensaje
        if (!e.detail.isLooking && currentGame) {
            showAttentionWarning();
        }
    });
    
    // NO inicializar EyeGestures aquí, esperar a que el usuario seleccione un juego
    const statusEl = document.getElementById('status');
    statusEl.textContent = '✅ Listo - Selecciona un juego para comenzar';
    statusEl.style.background = 'rgba(76, 175, 80, 0.3)';
    
    const cameraInfo = document.getElementById('camera-info');
    if (cameraInfo) {
        cameraInfo.style.display = 'block';
    }
}

function createAdvancedControls() {
    const panel = document.createElement('div');
    panel.id = 'advanced-controls';
    panel.style.position = 'fixed';
    panel.style.bottom = '20px';
    panel.style.right = '20px';
    panel.style.background = 'linear-gradient(135deg, rgba(29, 53, 87, 0.95) 0%, rgba(69, 123, 157, 0.95) 100%)';
    panel.style.color = '#f1faee';
    panel.style.padding = '20px';
    panel.style.borderRadius = '15px';
    panel.style.fontFamily = 'Arial, sans-serif';
    panel.style.fontSize = '14px';
    panel.style.zIndex = '9999';
    panel.style.minWidth = '280px';
    panel.style.boxShadow = '0 8px 32px rgba(69, 123, 157, 0.4)';
    panel.style.backdropFilter = 'blur(10px)';
    panel.style.border = '2px solid rgba(168, 218, 220, 0.3)';
    
    panel.innerHTML = `
        <h3 style="margin: 0 0 15px 0; font-size: 16px; border-bottom: 2px solid rgba(168, 218, 220, 0.5); padding-bottom: 8px; color: #f1faee;">
            ⚙️ Controles Avanzados
        </h3>
        <div style="margin: 10px 0;">
            <button id="toggle-trail-btn" class="advanced-btn" style="background: linear-gradient(135deg, #457b9d 0%, #1d3557 100%);">
                👁️ Rastro de Mirada: OFF
            </button>
        </div>
        <div style="margin: 10px 0;">
            <button id="toggle-heatmap-btn" class="advanced-btn" style="background: linear-gradient(135deg, #e63946 0%, #c1121f 100%);" disabled>
                🔥 Heatmap: OFF
            </button>
        </div>
        <div style="margin: 10px 0;">
            <button id="toggle-reading-btn" class="advanced-btn" style="background: linear-gradient(135deg, #a8dadc 0%, #457b9d 100%);">
                📖 Modo Lectura: OFF
            </button>
        </div>
        <div style="margin: 10px 0;">
            <button id="clear-trail-btn" class="advanced-btn" style="background: linear-gradient(135deg, #78909c 0%, #546e7a 100%);">
                🗑️ Limpiar Rastro
            </button>
        </div>
        <div style="margin: 15px 0 10px 0; padding-top: 10px; border-top: 1px solid rgba(168, 218, 220, 0.3);">
            <label style="display: block; margin-bottom: 5px; color: #f1faee;">Activar Eye Gestures:</label>
            <input type="checkbox" id="chkJustTrackWithEyes" style="width: 100%;">
        </div>
        <div style="margin: 15px 0 10px 0; padding-top: 10px; border-top: 1px solid rgba(168, 218, 220, 0.3);">
            <label style="display: block; margin-bottom: 5px; color: #f1faee;">📊 Precisión del Filtro:</label>
            <input type="range" id="filter-precision" min="1" max="20" value="5" style="width: 100%;">
            <small id="filter-value" style="color: #a8dadc;">Valor: 5</small>
        </div>
        <style>
            .advanced-btn {
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 10px;
                color: #f1faee;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 13px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }
            .advanced-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            }
            .advanced-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .advanced-btn.active {
                box-shadow: 0 0 20px rgba(168, 218, 220, 0.8);
                border: 2px solid #a8dadc;
            }
        </style>
    `;
    
    document.body.appendChild(panel);
    
    // Event listeners
    document.getElementById('toggle-trail-btn').addEventListener('click', toggleTrail);
    document.getElementById('toggle-heatmap-btn').addEventListener('click', toggleHeatmap);
    document.getElementById('toggle-reading-btn').addEventListener('click', toggleReading);
    document.getElementById('clear-trail-btn').addEventListener('click', clearTrail);
    document.getElementById('filter-precision').addEventListener('input', updateFilterPrecision);
     document.getElementById('chkJustTrackWithEyes').addEventListener('change', changeValue);
    // Actualizar UI inicial ya que el rastro está activado por defecto
    const trailBtn = document.getElementById('toggle-trail-btn');
    const heatmapBtn = document.getElementById('toggle-heatmap-btn');
    if (gazeTrail.enabled) {
        trailBtn.textContent = '👁️ Rastro de Mirada: ON';
        trailBtn.classList.add('active');
        heatmapBtn.disabled = false;
    }
}
window.advancedControls = window.advancedControls || {};

function _sysMouseToGame(e) {
    const x = e.clientX;
    const y = e.clientY;
    if (currentGame && typeof currentGame.onGaze === 'function') {
        currentGame.onGaze(x, y);
    }
}

function changeValue(){
    elem = document.getElementById('chkJustTrackWithEyes')
    window.advancedControls.justTrackWithEyes = elem.checked;

    // si globalGazeTrail ya existe, pedirle cambiar de modo
    valueBool = document.getElementById('chkJustTrackWithEyes').checked
    if (window.globalGazeTrail && typeof window.globalGazeTrail.setMode === 'function') {
        window.globalGazeTrail.setMode(!valueBool ? 'justTrackWithEyes' : 'eyeGestures');
    }

    if (!valueBool) {
        // stop EyeGestures if running (best-effort)
        try { if (eyeGestures && typeof eyeGestures.stop === 'function') eyeGestures.stop(); } catch(e){}
        // route system mouse to games
        window.addEventListener('mousemove', _sysMouseToGame, { passive: true });
    } else {
        window.removeEventListener('mousemove', _sysMouseToGame);
        // optionally re-init EyeGestures later when starting a game that needs it
    }
}

function toggleTrail() {
    if (!gazeTrail) return;
    
    gazeTrail.toggle();
    const btn = document.getElementById('toggle-trail-btn');
    const heatmapBtn = document.getElementById('toggle-heatmap-btn');
    
    if (gazeTrail.enabled) {
        btn.textContent = '👁️ Rastro de Mirada: ON';
        btn.classList.add('active');
        heatmapBtn.disabled = false;
    } else {
        btn.textContent = '👁️ Rastro de Mirada: OFF';
        btn.classList.remove('active');
        heatmapBtn.disabled = true;
    }
}

function toggleHeatmap() {
    if (!gazeTrail) return;
    
    gazeTrail.toggleHeatmap();
    const btn = document.getElementById('toggle-heatmap-btn');
    
    if (gazeTrail.showHeatmap) {
        btn.textContent = '🔥 Heatmap: ON';
        btn.classList.add('active');
    } else {
        btn.textContent = '🔥 Heatmap: OFF';
        btn.classList.remove('active');
    }
}

function toggleReading() {
    if (!readingDetector) return;
    
    readingDetector.toggle();
    const btn = document.getElementById('toggle-reading-btn');
    
    if (readingDetector.enabled) {
        btn.textContent = '📖 Modo Lectura: ON';
        btn.classList.add('active');
    } else {
        btn.textContent = '📖 Modo Lectura: OFF';
        btn.classList.remove('active');
    }
}

function clearTrail() {
    if (!gazeTrail) return;
    gazeTrail.clear();
}

function updateFilterPrecision(e) {
    const value = parseInt(e.target.value);
    document.getElementById('filter-value').textContent = `Valor: ${value}`;
    
    if (gazeFilter) {
        gazeFilter.measurementNoise = value;
        gazeFilter.reset();
    }
}

function initEyeGestures() {
    return new Promise(async (resolve, reject) => {
        const statusEl = document.getElementById('status');
        const cameraStatus = document.getElementById('camera-status');
        
        if (eyeGestures) {
            // Ya está inicializado
            console.log('EyeGestures ya está inicializado');
            resolve();
            return;
        }
        
        try {
            console.log('=== INICIANDO EyeGestures ===');
            
            // Callback que se ejecuta en cada frame con la posición de la mirada
            function onGazePoint(point, calibration) {
                let x = point[0];
                let y = point[1];
                
                // MEJORA 1: Aplicar filtro de Kalman para suavizar
                if (gazeFilter) {
                    const filtered = gazeFilter.filter(x, y);
                    x = filtered.x;
                    y = filtered.y;
                    
                    // Mostrar stats del filtro en consola (solo cada 30 frames)
                    if (gazeFilter.frameCount % 30 === 0) {
                        const stats = gazeFilter.getStats();
                        if (stats) {
                            console.log('📊 Filtro:', stats);
                        }
                    }
                }
                
                // MEJORA 2: Añadir punto al rastro visual
                if (gazeTrail && gazeTrail.enabled && !calibration) {
                    // Solo mostrar rastro cuando no estamos en calibración
                    const intensity = gazeFilter ? (1.0 - gazeFilter.getVelocity() / 1000) : 1.0;
                    gazeTrail.addPoint(x, y, Math.max(0.3, Math.min(1.0, intensity)));
                }
                
                // MEJORA 3: Detectar lectura
                if (readingDetector && readingDetector.enabled && !calibration) {
                    readingDetector.addGazePoint(x, y);
                }
                
                // Notificar al time tracker
                if (timeTracker) {
                    timeTracker.onGazeDetected(x, y);
                }
                
                // Pasar al juego actual si existe (usar posición filtrada)
                if (currentGame && currentGame.onGaze) {
                    currentGame.onGaze(x, y);
                }
            }
            
            statusEl.textContent = '📹 Solicitando acceso a la cámara...';
            statusEl.style.background = 'rgba(255, 193, 7, 0.3)';
            
            if (cameraStatus) {
                cameraStatus.textContent = '⏳ Inicializando...';
                cameraStatus.style.color = '#FFC107';
            }
            
            // Crear instancia de EyeGestures
            console.log('Creando instancia de EyeGestures...');
            eyeGestures = new EyeGestures("video", onGazePoint);
            
            // Configurar para que sea invisible (sin logo)
            eyeGestures.invisible();
            
            console.log('EyeGestures creado, esperando inicialización...');
            
            // Esperar a que init() complete (es asíncrono)
            // Verificar cada 500ms si la cámara está activa
            let checkAttempts = 0;
            const maxAttempts = 20; // 10 segundos máximo
            
            const checkInit = setInterval(() => {
                checkAttempts++;
                console.log(`Verificando inicialización... Intento ${checkAttempts}/${maxAttempts}`);
                
                const video = document.getElementById('video');
                
                // Verificar si el video tiene stream
                if (video && video.srcObject && video.srcObject.active) {
                    clearInterval(checkInit);
                    console.log('✅ Cámara detectada y activa!');
                    
                    statusEl.textContent = '✅ Cámara activa y lista';
                    statusEl.style.background = 'rgba(76, 175, 80, 0.3)';
                    
                    if (cameraStatus) {
                        cameraStatus.textContent = '✅ Cámara detectada correctamente';
                        cameraStatus.style.color = '#4CAF50';
                    }
                    
                    resolve();
                } else if (checkAttempts >= maxAttempts) {
                    clearInterval(checkInit);
                    const error = new Error('Timeout: La cámara no se activó en el tiempo esperado');
                    console.error(error);
                    reject(error);
                }
            }, 500);
            
        } catch (error) {
            console.error('❌ Error al inicializar EyeGestures:', error);
            statusEl.textContent = '❌ Error: ' + error.message;
            statusEl.style.background = 'rgba(255, 87, 87, 0.3)';
            
            if (cameraStatus) {
                cameraStatus.textContent = '❌ Error de inicialización';
                cameraStatus.style.color = '#ff5757';
            }
            
            reject(error);
        }
    });
}

// Función para probar la cámara manualmente
async function testCamera() {
    const btn = document.getElementById('test-camera-btn');
    const originalText = btn.textContent;
    const statusEl = document.getElementById('status');
    const cameraStatus = document.getElementById('camera-status');
    
    console.log('=== TEST DE CÁMARA INICIADO ===');
    
    try {
        btn.textContent = '⏳ Probando...';
        btn.disabled = true;
        
        if (statusEl) {
            statusEl.textContent = '🧪 Probando acceso a cámara...';
            statusEl.style.background = 'rgba(255, 193, 7, 0.3)';
        }
        
        if (cameraStatus) {
            cameraStatus.textContent = '🔍 Verificando permisos...';
            cameraStatus.style.color = '#FFC107';
        }
        
        console.log('Solicitando getUserMedia...');
        
        // Solicitar acceso a la cámara con más detalles
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: 'user',
                width: { ideal: 640 },
                height: { ideal: 480 }
            } 
        });
        
        console.log('✅ Stream obtenido:', stream);
        console.log('- Video tracks:', stream.getVideoTracks().length);
        
        const videoTracks = stream.getVideoTracks();
        if (videoTracks.length > 0) {
            const track = videoTracks[0];
            console.log('- Label:', track.label);
            console.log('- Estado:', track.readyState);
            console.log('- Settings:', track.getSettings());
        }
        
        btn.textContent = '✅ ¡Funciona!';
        btn.style.background = 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)';
        
        if (statusEl) {
            statusEl.textContent = '✅ Cámara funcionando correctamente';
            statusEl.style.background = 'rgba(76, 175, 80, 0.3)';
        }
        
        if (cameraStatus) {
            cameraStatus.textContent = '✅ ' + (videoTracks[0]?.label || 'Cámara detectada');
            cameraStatus.style.color = '#4CAF50';
        }
        
        // Mostrar preview por 3 segundos
        const video = document.getElementById('video');
        video.srcObject = stream;
        await video.play();
        
        video.style.display = 'block';
        video.style.position = 'fixed';
        video.style.bottom = '20px';
        video.style.right = '20px';
        video.style.width = '240px';
        video.style.height = 'auto';
        video.style.border = '4px solid #4CAF50';
        video.style.borderRadius = '15px';
        video.style.zIndex = '9999';
        video.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.5)';
        
        // Añadir texto sobre el video
        const overlay = document.createElement('div');
        overlay.id = 'video-overlay';
        overlay.style.position = 'fixed';
        overlay.style.bottom = '270px';
        overlay.style.right = '20px';
        overlay.style.background = 'rgba(76, 175, 80, 0.95)';
        overlay.style.color = 'white';
        overlay.style.padding = '10px 20px';
        overlay.style.borderRadius = '10px';
        overlay.style.zIndex = '10000';
        overlay.style.fontWeight = 'bold';
        overlay.textContent = '✅ Cámara funcionando correctamente';
        document.body.appendChild(overlay);
        
        setTimeout(() => {
            video.style.display = 'none';
            stream.getTracks().forEach(track => {
                track.stop();
                console.log('Track detenido:', track.label);
            });
            overlay.remove();
            btn.textContent = originalText;
            btn.disabled = false;
            btn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            console.log('=== TEST DE CÁMARA FINALIZADO ===');
        }, 3000);
        
    } catch (error) {
        console.error('❌ ERROR DE CÁMARA:', error);
        console.error('- Nombre:', error.name);
        console.error('- Mensaje:', error.message);
        console.error('- Stack:', error.stack);
        
        btn.textContent = '❌ Error';
        btn.style.background = 'linear-gradient(135deg, #ff5757 0%, #c62828 100%)';
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.disabled = false;
            btn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }, 3000);
        
        // Mensaje de error más detallado
        let errorMsg = '❌ No se pudo acceder a la cámara.\n\n';
        let shortMsg = 'Error desconocido';
        
        if (error.name === 'NotAllowedError') {
            shortMsg = 'Permiso denegado';
            errorMsg += '🚫 Permisos denegados.\n\nSolución:\n' +
                       '1. Haz clic en el ícono de cámara en la barra de direcciones\n' +
                       '2. Permite el acceso a la cámara\n' +
                       '3. Recarga la página';
        } else if (error.name === 'NotFoundError') {
            shortMsg = 'No se encontró cámara';
            errorMsg += '📹 No se encontró ninguna cámara.\n\nVerifica:\n' +
                       '1. Que tu dispositivo tenga cámara\n' +
                       '2. Que esté conectada correctamente\n' +
                       '3. Que ninguna otra app la esté usando';
        } else if (error.name === 'NotReadableError') {
            shortMsg = 'Cámara en uso';
            errorMsg += '⚠️ Cámara en uso por otra aplicación.\n\nCierra:\n' +
                       '1. Zoom, Teams, Skype\n' +
                       '2. Otras pestañas del navegador\n' +
                       '3. Aplicaciones de cámara';
        } else if (error.name === 'SecurityError') {
            shortMsg = 'Error de seguridad';
            errorMsg += '🔒 Error de seguridad.\n\nAsegúrate de:\n' +
                       '1. Usar localhost o HTTPS\n' +
                       '2. No usar file:// (usa un servidor)\n' +
                       '3. Navegar en modo normal (no privado)';
        } else {
            shortMsg = error.message;
            errorMsg += 'Error: ' + error.message + '\n\n' +
                       'Asegúrate de estar usando:\n' +
                       '• http://localhost (no file://)\n' +
                       '• Un navegador moderno actualizado';
        }
        
        if (statusEl) {
            statusEl.textContent = '❌ ' + shortMsg;
            statusEl.style.background = 'rgba(255, 87, 87, 0.3)';
        }
        
        if (cameraStatus) {
            cameraStatus.textContent = '❌ ' + error.name + ': ' + shortMsg;
            cameraStatus.style.color = '#ff5757';
        }
        
        alert(errorMsg);
        console.log('=== TEST DE CÁMARA FINALIZADO CON ERROR ===');
    }
}

function showAttentionWarning() {
    // Mostrar advertencia visual cuando el usuario no está mirando
    const warning = document.createElement('div');
    warning.id = 'attention-warning';
    warning.style.position = 'fixed';
    warning.style.top = '50%';
    warning.style.left = '50%';
    warning.style.transform = 'translate(-50%, -50%)';
    warning.style.background = 'rgba(255, 87, 87, 0.95)';
    warning.style.color = 'white';
    warning.style.padding = '30px 50px';
    warning.style.borderRadius = '20px';
    warning.style.fontSize = '1.5rem';
    warning.style.fontWeight = 'bold';
    warning.style.zIndex = '10000';
    warning.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.5)';
    warning.textContent = '👀 ¡Sigue mirando la pantalla!';
    
    document.body.appendChild(warning);
    
    // Remover después de 2 segundos
    setTimeout(() => {
        if (warning.parentNode) {
            warning.remove();
        }
    }, 2000);
}

function startGame(gameType) {
    console.log('Iniciando juego:', gameType);
    valueBool = document.getElementById('chkJustTrackWithEyes').checked
    // Primero inicializar EyeGestures si no está listo
    if (!eyeGestures && valueBool) {
        const statusEl = document.getElementById('status');
        statusEl.textContent = '⏳ Preparando sistema...';
        
        initEyeGestures().then(() => {
            // Ahora sí, continuar con el juego
            setupAndStartGame(gameType);
        }).catch(error => {
            alert('❌ Error al inicializar el sistema de seguimiento ocular.\n\n' + 
                  'Por favor:\n' +
                  '1. Permite el acceso a la cámara\n' +
                  '2. Asegúrate de usar localhost\n' +
                  '3. Recarga la página e intenta de nuevo');
            console.error(error);
        });
    } else {
        setupAndStartGame(gameType);
    }
}

function setupAndStartGame(gameType) {
    console.log('Configurando juego:', gameType);
    
    // Ocultar menú principal
    document.getElementById('main-menu').style.display = 'none';
    let useEyeMouse = document.getElementById('chkJustTrackWithEyes').checked;
    // Mostrar contenedor de juego
    const gameContainer = document.getElementById('game-container');
    gameContainer.style.display = 'block';
    
    // Obtener canvas
    const canvas = document.getElementById('game-canvas');
    
    // Configurar título
    const gameTitle = document.getElementById('game-title');
    const gameTitles = {
        'pong': '🏓 Eye Pong',
        'target': '🎯 Eye Target',
        'snake': '🐍 Eye Snake',
        'collect': '⭐ Eye Collect'
    };
    gameTitle.textContent = gameTitles[gameType] || 'Juego';
    
    // Resetear puntuación
    document.getElementById('score').textContent = '0';
    document.getElementById('game-info').innerHTML = '';
    // SI NO ESTÁ CALIBRADO, PRIMERO CALIBRAR
    if (!isCalibrated && useEyeMouse) {
        console.log('Iniciando calibración...');
        
        // Mostrar mensaje
        const gameInfo = document.getElementById('game-info');
        gameInfo.innerHTML = '<div style="color: white; font-size: 20px; margin-top: 20px;">⏳ Preparando calibración...</div>';
        
        // Iniciar EyeGestures (esto activa la cámara y muestra el overlay de calibración)
        eyeGestures.start();
        
        // Esperar a que la calibración esté completa (25 puntos)
        // El usuario verá el overlay automáticamente
        let calibCheckInterval = setInterval(() => {
            // Verificar si la calibración está completa
            if (eyeGestures.calib_counter >= eyeGestures.calib_max) {
                clearInterval(calibCheckInterval);
                isCalibrated = true;
                console.log('✅ Calibración completada!');
                
                createAndStartGame(gameType, canvas);
            }
        }, 500);
        
    } else if (isCalibrated || !useEyeMouse) {
        createAndStartGame(gameType, canvas);
    } else {
        alert('❌ Error: Sistema de seguimiento no inicializado');
        backToMenu();
    }
}

function createAndStartGame(gameType, canvas) {
    console.log('Creando juego:', gameType);
    
    function gazeCallback(x, y) {
    if (currentGame && currentGame.onGaze) {
            currentGame.onGaze(x, y);
        }
        print("X; Y 0 ", x + ', ' + y)
    }
    
    // Crear instancia del juego
    switch(gameType) {
        case 'pong':
            currentGame = new EyePong(canvas, gazeCallback);
            break;
        case 'target':
            currentGame = new EyeTarget(canvas, gazeCallback);
            break;
        case 'snake':
            currentGame = new EyeSnake(canvas, gazeCallback);
            break;
        case 'collect':
            currentGame = new EyeCollect(canvas, gazeCallback);
            break;
        default:
            console.error('Tipo de juego desconocido:', gameType);
            backToMenu();
            return;
    }
    
    // Iniciar el juego
    if (currentGame && currentGame.start) {
        console.log('🎮 Iniciando juego...');
        currentGame.start();
    }
}

function backToMenu() {
    console.log('Volviendo al menú...');
    
    // Detener juego actual
    if (currentGame) {
        if (currentGame.destroy) {
            currentGame.destroy();
        }
        currentGame = null;
    }
    
    document.getElementById('game-container').style.display = 'none';
    
    document.getElementById('main-menu').style.display = 'block';
}

window.startGame = startGame;
window.backToMenu = backToMenu;
window.testCamera = testCamera;

console.log('Main.js cargado correctamente');
console.log('Funciones globales registradas:', {
    startGame: typeof window.startGame,
    backToMenu: typeof window.backToMenu,
    testCamera: typeof window.testCamera
});
console.log('EyeGestures disponible:', typeof window.EyeGestures);

// Manejo de errores global
window.addEventListener('error', (e) => {
    console.error('Error global:', e.error);
});

// Limpiar al cerrar
window.addEventListener('beforeunload', () => {
    if (currentGame && currentGame.destroy) {
        currentGame.destroy();
    }
    if (timeTracker && timeTracker.destroy) {
        timeTracker.destroy();
    }
});

console.log('Main.js cargado correctamente');
