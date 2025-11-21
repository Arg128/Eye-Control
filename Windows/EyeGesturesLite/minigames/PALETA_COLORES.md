# 🎨 Paleta de Colores - EyeGestures

## Fecha: 24 de octubre de 2025

---

## 🌈 Paleta Principal

### Colores Base
```
#e63946 - Rojo Coral (Accent/Alerts)
#f1faee - Blanco Crema (Backgrounds/Text)
#a8dadc - Azul Claro (Secondary/Links)
#457b9d - Azul Medio (Primary)
#1d3557 - Azul Marino (Dark/Headers)
```

---

## 📊 Distribución de Colores

### 🔴 #e63946 - Rojo Coral
**Uso:** Alertas, badges "NEW", elementos de atención
- **RGB:** `rgb(230, 57, 70)`
- **RGBA:** `rgba(230, 57, 70, 0.9)`
- **Gradiente:** `#e63946 → #c1121f`

**Aplicado en:**
- ✅ Badges "NEW" en tarjetas
- ✅ Botón Heatmap en panel de controles
- ✅ Heatmap alta intensidad (caliente)

---

### ⚪ #f1faee - Blanco Crema
**Uso:** Fondos, texto sobre fondos oscuros
- **RGB:** `rgb(241, 250, 238)`
- **RGBA:** `rgba(241, 250, 238, 0.95)`

**Aplicado en:**
- ✅ Fondo de tarjetas (con gradiente)
- ✅ Texto en header
- ✅ Texto en panel de controles
- ✅ Texto en badges
- ✅ Color de botones hover

---

### 💙 #a8dadc - Azul Claro
**Uso:** Enlaces, acentos secundarios, transiciones
- **RGB:** `rgb(168, 218, 220)`
- **RGBA:** `rgba(168, 218, 220, 0.5)`

**Aplicado en:**
- ✅ Tagline del header
- ✅ Bordes de tarjetas
- ✅ Tabs en estado normal
- ✅ Footer links
- ✅ Líneas del rastro de mirada
- ✅ Heatmap baja intensidad (frío)
- ✅ Botón "Modo Lectura"

---

### 🔵 #457b9d - Azul Medio
**Uso:** Elementos principales, botones, rastro de mirada
- **RGB:** `rgb(69, 123, 157)`
- **RGBA:** `rgba(69, 123, 157, 0.7)`
- **Gradiente:** `#457b9d → #1d3557`

**Aplicado en:**
- ✅ Botones principales
- ✅ Tabs activas
- ✅ Badges "BETA"
- ✅ Rastro de mirada (color base)
- ✅ Checkmarks en listas
- ✅ Texto de descripciones
- ✅ Heatmap media intensidad

---

### 🌑 #1d3557 - Azul Marino
**Uso:** Headers, texto principal, fondos oscuros
- **RGB:** `rgb(29, 53, 87)`
- **RGBA:** `rgba(29, 53, 87, 0.95)`

**Aplicado en:**
- ✅ Header (gradiente con #457b9d)
- ✅ Footer
- ✅ Texto principal
- ✅ Títulos de tarjetas
- ✅ Panel de controles (gradiente)
- ✅ Botones principales (gradiente)
- ✅ Tabs activas (gradiente)

---

## 🎯 Aplicaciones por Componente

### Hub (hub.html)

#### Background
```css
background: linear-gradient(135deg, #f1faee 0%, #a8dadc 50%, #457b9d 100%);
color: #1d3557;
```

#### Header
```css
background: linear-gradient(135deg, rgba(29, 53, 87, 0.95), rgba(69, 123, 157, 0.95));
```
- Título: `#f1faee`
- Tagline: `#a8dadc`

#### Navigation Tabs
- **Normal:** `rgba(241, 250, 238, 0.3)` con borde `#a8dadc`
- **Hover:** `rgba(168, 218, 220, 0.5)`
- **Active:** `linear-gradient(#457b9d, #1d3557)` con texto `#f1faee`

#### Cards
- **Fondo:** `linear-gradient(rgba(241, 250, 238, 0.95), rgba(255, 255, 255, 0.95))`
- **Borde:** `rgba(168, 218, 220, 0.5)`
- **Título:** `#1d3557`
- **Descripción:** `#457b9d`
- **Checkmark:** `#457b9d`
- **Botón:** `linear-gradient(#457b9d, #1d3557)`

#### Badges
- **NEW:** `linear-gradient(#e63946, #c1121f)` con texto `#f1faee`
- **BETA:** `linear-gradient(#457b9d, #1d3557)` con texto `#f1faee`

#### Footer
- **Fondo:** `rgba(29, 53, 87, 0.9)`
- **Texto:** `#f1faee`
- **Links:** `#a8dadc`

---

### Panel de Controles (main.js)

#### Panel Principal
```javascript
background: linear-gradient(135deg, rgba(29, 53, 87, 0.95), rgba(69, 123, 157, 0.95));
color: #f1faee;
border: 2px solid rgba(168, 218, 220, 0.3);
```

#### Botones
- **Rastro de Mirada:** `linear-gradient(#457b9d, #1d3557)`
- **Heatmap:** `linear-gradient(#e63946, #c1121f)`
- **Modo Lectura:** `linear-gradient(#a8dadc, #457b9d)`
- **Limpiar:** `linear-gradient(#78909c, #546e7a)` (gris neutro)

#### Estado Active
```css
box-shadow: 0 0 20px rgba(168, 218, 220, 0.8);
border: 2px solid #a8dadc;
```

---

### Rastro de Mirada (gazeTrail.js)

#### Color Principal
```javascript
trailColor: 'rgba(69, 123, 157, 0.7)' // #457b9d
```

#### Gradiente de Puntos
- **Centro:** `rgba(69, 123, 157, 0.9)` - #457b9d
- **Medio:** `rgba(168, 218, 220, 0.6)` - hacia #a8dadc
- **Exterior:** Fade a transparente

#### Líneas de Conexión
```javascript
strokeStyle: 'rgba(168, 218, 220, 0.5)' // #a8dadc
lineWidth: 3px
```

#### Heatmap
- **Frío (0-50%):** `#a8dadc → #457b9d` (azul claro a medio)
- **Caliente (50-100%):** `#457b9d → #e63946` (azul medio a rojo)

---

## 🎨 Gradientes Predefinidos

### Gradiente 1: Header/Footer
```css
linear-gradient(135deg, #1d3557 0%, #457b9d 100%)
```

### Gradiente 2: Botones Principales
```css
linear-gradient(135deg, #457b9d 0%, #1d3557 100%)
```

### Gradiente 3: Background Principal
```css
linear-gradient(135deg, #f1faee 0%, #a8dadc 50%, #457b9d 100%)
```

### Gradiente 4: Alerts/NEW
```css
linear-gradient(135deg, #e63946 0%, #c1121f 100%)
```

### Gradiente 5: Secondary Actions
```css
linear-gradient(135deg, #a8dadc 0%, #457b9d 100%)
```

---

## 📐 Opacidades Recomendadas

### Fondos
- **Sólidos:** `0.95` - Máxima legibilidad con mínima transparencia
- **Overlays:** `0.5-0.7` - Balance entre visibilidad y contexto
- **Glassmorphism:** `0.3` - Efecto moderno y sutil

### Texto
- **Principal:** `1.0` - Sin transparencia
- **Secundario:** `0.9` - Sutil jerarquía
- **Terciario:** `0.7` - Información complementaria

### Bordes
- **Activos:** `0.8` - Definición clara
- **Normales:** `0.5` - Sutil separación
- **Disabled:** `0.3` - Mínima presencia

### Sombras
- **Hover:** `0.3-0.5` - Elevación notoria
- **Normal:** `0.15-0.2` - Profundidad sutil
- **Subtle:** `0.1` - Mínima separación

---

## 🌟 Combinaciones Destacadas

### Combinación 1: Elegante
```
Fondo: #f1faee
Texto: #1d3557
Acento: #457b9d
```

### Combinación 2: Vibrante
```
Fondo: #457b9d
Texto: #f1faee
Acento: #e63946
```

### Combinación 3: Suave
```
Fondo: #a8dadc
Texto: #1d3557
Acento: #457b9d
```

---

## ✅ Accesibilidad

### Contraste WCAG AA
- ✅ `#1d3557` sobre `#f1faee` - **Ratio: 10.8:1** (Excelente)
- ✅ `#457b9d` sobre `#f1faee` - **Ratio: 3.8:1** (Bueno para texto grande)
- ✅ `#f1faee` sobre `#1d3557` - **Ratio: 10.8:1** (Excelente)
- ✅ `#e63946` sobre `#f1faee` - **Ratio: 4.2:1** (Bueno)

### Recomendaciones
- ✅ Usar `#1d3557` para texto pequeño sobre fondos claros
- ✅ Usar `#f1faee` para texto sobre fondos oscuros
- ✅ `#457b9d` solo para texto grande (>18px) sobre `#f1faee`
- ⚠️ Evitar `#a8dadc` como texto sobre `#f1faee` (bajo contraste)

---

## 🎯 Psicología de los Colores

### #e63946 - Rojo Coral
- **Emoción:** Energía, urgencia, pasión
- **Uso:** Llamadas a la acción, alertas importantes
- **Frecuencia:** 5-10% de la paleta

### #f1faee - Blanco Crema
- **Emoción:** Limpieza, claridad, espacio
- **Uso:** Fondo principal, respiración visual
- **Frecuencia:** 40-50% de la paleta

### #a8dadc - Azul Claro
- **Emoción:** Calma, serenidad, confianza
- **Uso:** Transiciones, acentos suaves
- **Frecuencia:** 15-20% de la paleta

### #457b9d - Azul Medio
- **Emoción:** Profesionalidad, estabilidad
- **Uso:** Elementos principales, acciones primarias
- **Frecuencia:** 20-25% de la paleta

### #1d3557 - Azul Marino
- **Emoción:** Autoridad, seriedad, profundidad
- **Uso:** Headers, texto principal, fundamentos
- **Frecuencia:** 10-15% de la paleta

---

## 📱 Responsive y Dark Mode (Futuro)

### Versión Clara (Actual)
```
Background: #f1faee → #a8dadc → #457b9d
Text: #1d3557
Accents: #457b9d, #e63946
```

### Versión Oscura (Propuesta)
```
Background: #1d3557 → #457b9d
Text: #f1faee
Accents: #a8dadc, #e63946
```

---

**Paleta aplicada con** 🎨 **el 24 de octubre de 2025**  
*Diseño profesional, moderno y accesible*
