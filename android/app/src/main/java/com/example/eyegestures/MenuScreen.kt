package com.example.eyegestures

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * Pantalla de Menú Principal
 * Muestra dos botones grandes para seleccionar el juego
 */
@Composable
fun MenuScreen(
    onNavigateToMaze: () -> Unit,
    onNavigateToSnake: () -> Unit,
    onNavigateToCalibration: () -> Unit = {}
) {
    // Observar el estado de calibración y posición del cursor
    val isCalibrated by GazeCursorManager.isCalibrated.collectAsState()
    val gazePosition by GazeCursorManager.gazePosition.collectAsState()
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF1a1a2e),
                        Color(0xFF16213e),
                        Color(0xFF0f3460)
                    )
                )
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Logo/Título
            MenuHeader()
            
            Spacer(modifier = Modifier.height(48.dp))
            
            // Botón de Laberinto
            GameMenuButton(
                title = "🧩 LABERINTO",
                description = "Encuentra el camino a la meta",
                icon = Icons.Default.Star,
                gradient = listOf(Color(0xFF00BCD4), Color(0xFF0097A7)),
                onClick = onNavigateToMaze,
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Botón de Snake
            GameMenuButton(
                title = "🐍 SNAKE",
                description = "Come y crece sin chocar",
                icon = Icons.Default.PlayArrow,
                gradient = listOf(Color(0xFF4CAF50), Color(0xFF388E3C)),
                onClick = onNavigateToSnake,
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Botón de Calibración con indicador de estado
            CalibrationMenuButton(
                isCalibrated = isCalibrated,
                onClick = onNavigateToCalibration,
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(48.dp))
            
            // Info de Eye Gestures
            MenuFooter()
        }
        
        // Cursor de mirada superpuesto (solo si está calibrado)
        if (isCalibrated) {
            GazeCursor(
                gazePosition = gazePosition,
                isVisible = true
            )
        }
    }
}

/**
 * Header del menú con título y subtítulo
 */
@Composable
fun MenuHeader() {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Emoji grande
        Text(
            text = "👁️",
            fontSize = 72.sp,
            textAlign = TextAlign.Center
        )
        
        // Título principal
        Text(
            text = "EYE GESTURES",
            fontSize = 36.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White,
            textAlign = TextAlign.Center
        )
        
        // Subtítulo
        Text(
            text = "Juega con la Mirada",
            fontSize = 18.sp,
            color = Color.White.copy(alpha = 0.7f),
            textAlign = TextAlign.Center
        )
        
        // Versión
        Text(
            text = "v1.0 - Android Edition",
            fontSize = 12.sp,
            color = Color.White.copy(alpha = 0.5f),
            textAlign = TextAlign.Center
        )
    }
}

/**
 * Botón de juego con gradiente y estilo personalizado
 */
@Composable
fun GameMenuButton(
    title: String,
    description: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    gradient: List<Color>,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .height(140.dp)
            .shadow(8.dp, RoundedCornerShape(16.dp)),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.Transparent
        ),
        onClick = onClick
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.horizontalGradient(gradient)
                )
                .padding(20.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxSize(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                // Contenido del botón
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = title,
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = description,
                        fontSize = 14.sp,
                        color = Color.White.copy(alpha = 0.9f)
                    )
                }
                
                // Ícono
                Icon(
                    imageVector = icon,
                    contentDescription = title,
                    modifier = Modifier.size(48.dp),
                    tint = Color.White.copy(alpha = 0.8f)
                )
            }
        }
    }
}

/**
 * Footer con información adicional
 */
@Composable
fun MenuFooter() {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Divider(
            modifier = Modifier.width(200.dp),
            color = Color.White.copy(alpha = 0.3f)
        )
        
        Text(
            text = "Controles disponibles:",
            fontSize = 14.sp,
            color = Color.White.copy(alpha = 0.7f),
            fontWeight = FontWeight.Bold
        )
        
        Row(
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            ControlBadge("👁️ Mirada")
            ControlBadge("👆 Táctil")
            ControlBadge("😉 Parpadeo")
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "Powered by ML Kit Face Detection",
            fontSize = 10.sp,
            color = Color.White.copy(alpha = 0.4f),
            textAlign = TextAlign.Center
        )
    }
}

/**
 * Botón de calibración con indicador de estado
 */
@Composable
fun CalibrationMenuButton(
    isCalibrated: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val gradient = if (isCalibrated) {
        listOf(Color(0xFF4CAF50), Color(0xFF388E3C))  // Verde si calibrado
    } else {
        listOf(Color(0xFFFF9800), Color(0xFFF57C00))  // Naranja si no calibrado
    }
    
    val statusText = if (isCalibrated) "✓ Calibrado" else "⚠ Sin calibrar"
    val statusColor = if (isCalibrated) Color(0xFF4CAF50) else Color(0xFFFF9800)
    
    Card(
        modifier = modifier
            .height(120.dp)
            .shadow(8.dp, RoundedCornerShape(16.dp)),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.Transparent)
    ) {
        Button(
            onClick = onClick,
            modifier = Modifier
                .fillMaxSize()
                .background(Brush.horizontalGradient(gradient)),
            colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent),
            shape = RoundedCornerShape(16.dp),
            contentPadding = PaddingValues(20.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(
                    horizontalAlignment = Alignment.Start,
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = "⚙️ CALIBRACIÓN",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                    Text(
                        text = "Configura tu seguimiento ocular",
                        fontSize = 14.sp,
                        color = Color.White.copy(alpha = 0.9f)
                    )
                    
                    // Indicador de estado
                    Surface(
                        shape = RoundedCornerShape(8.dp),
                        color = Color.White.copy(alpha = 0.2f)
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = if (isCalibrated) Icons.Default.CheckCircle else Icons.Default.Warning,
                                contentDescription = null,
                                tint = statusColor,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = statusText,
                                fontSize = 12.sp,
                                color = Color.White,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
                
                Icon(
                    imageVector = Icons.Default.Visibility,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(48.dp)
                )
            }
        }
    }
}

/**
 * Badge pequeño para mostrar tipos de control
 */
@Composable
fun ControlBadge(text: String) {
    Surface(
        shape = RoundedCornerShape(12.dp),
        color = Color.White.copy(alpha = 0.1f)
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            fontSize = 12.sp,
            color = Color.White.copy(alpha = 0.8f)
        )
    }
}

/**
 * Variante alternativa del menú con diseño vertical compacto
 */
@Composable
fun CompactMenuScreen(
    onNavigateToMaze: () -> Unit,
    onNavigateToSnake: () -> Unit,
    onNavigateToSettings: (() -> Unit)? = null
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF1a1a2e))
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.SpaceEvenly
    ) {
        // Título compacto
        Text(
            text = "👁️ Eye Gestures",
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )
        
        // Botones de juegos
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            OutlinedButton(
                onClick = onNavigateToMaze,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(80.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.outlinedButtonColors(
                    containerColor = Color(0xFF00BCD4).copy(alpha = 0.2f)
                )
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text("🧩", fontSize = 32.sp)
                    Column {
                        Text(
                            "LABERINTO",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                        Text(
                            "Encuentra la salida",
                            fontSize = 12.sp,
                            color = Color.White.copy(alpha = 0.7f)
                        )
                    }
                }
            }
            
            OutlinedButton(
                onClick = onNavigateToSnake,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(80.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.outlinedButtonColors(
                    containerColor = Color(0xFF4CAF50).copy(alpha = 0.2f)
                )
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text("🐍", fontSize = 32.sp)
                    Column {
                        Text(
                            "SNAKE",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                        Text(
                            "Come y crece",
                            fontSize = 12.sp,
                            color = Color.White.copy(alpha = 0.7f)
                        )
                    }
                }
            }
            
            // Botón de configuración opcional
            onNavigateToSettings?.let { onSettings ->
                TextButton(
                    onClick = onSettings,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(
                        Icons.Default.Settings,
                        contentDescription = "Configuración",
                        tint = Color.White.copy(alpha = 0.6f)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        "Configuración",
                        color = Color.White.copy(alpha = 0.6f)
                    )
                }
            }
        }
    }
}
