# 🎮 Cómo Iniciar los Minijuegos

## 🚀 Opción 1: Usar el archivo .bat (MÁS FÁCIL)

### Con Node.js:
Simplemente haz **doble clic** en:
```
START_MINIGAMES.bat
```
Esto abrirá automáticamente el launcher en tu navegador.

### Con Python:
Si no tienes Node.js, haz **doble clic** en:
```
START_MINIGAMES_PYTHON.bat
```

---

## 🚀 Opción 2: Usar npm (requiere Node.js)

```powershell
npm start
```

Esto iniciará el servidor y abrirá automáticamente:
`http://localhost:8000/minigames/launcher.html`

### Otros comandos disponibles:

```powershell
# Solo iniciar el servidor (sin abrir navegador)
npm run serve

# Abrir directamente los minijuegos
npm run minigames

# Abrir la guía rápida
npm run quickstart
```

---

## 🚀 Opción 3: Manual

### Con Node.js:
```powershell
npx http-server -p 8000
```
Luego abre: `http://localhost:8000/minigames/`

### Con Python:
```powershell
python -m http.server 8000
```
Luego abre: `http://localhost:8000/minigames/`

---

## 📋 Requisitos

Para cualquier opción necesitas:
- ✅ Una cámara web funcional
- ✅ Navegador moderno (Chrome, Edge, Firefox)
- ✅ Buena iluminación

Y **UNA** de estas opciones:
- Node.js instalado → [Descargar aquí](https://nodejs.org/)
- Python instalado → [Descargar aquí](https://www.python.org/)

---

## ❌ Solución de Problemas

### "npm start" no funciona:
1. **Instala Node.js** si no lo tienes
2. O usa el archivo `START_MINIGAMES_PYTHON.bat`
3. O usa Python manualmente: `python -m http.server 8000`

### La cámara no funciona:
1. Verifica que diste permisos en el navegador
2. **IMPORTANTE**: Necesitas usar `http://localhost` (no `file://`)
3. Cierra otras aplicaciones que usen la cámara (Zoom, Teams, etc.)

### Error "EADDRINUSE" (puerto ocupado):
El puerto 8000 ya está en uso. Opciones:
1. Cierra el otro servidor
2. Usa otro puerto: `npx http-server -p 8080`

---

## 📖 Documentación Completa

Para más información, lee:
- `minigames/README.md` - Documentación completa de los juegos
- `minigames/QUICKSTART.html` - Guía interactiva de inicio

---

## 🎮 ¡A Jugar!

Una vez iniciado el servidor, visita:
- **Guía rápida**: http://localhost:8000/minigames/QUICKSTART.html
- **Minijuegos**: http://localhost:8000/minigames/index.html

**¡Controla los juegos con tu mirada!** 👀🎮
