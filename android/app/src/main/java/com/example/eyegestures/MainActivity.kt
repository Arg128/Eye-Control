package com.example.eyegestures

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import android.util.Log

class MainActivity : ComponentActivity() {
    
    // Launcher para solicitar permisos
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            // Permiso concedido
            recreate() // Reiniciar activity para aplicar cambios
        } else {
            // Permiso denegado
            // El usuario verá la pantalla de solicitud de permisos
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContent {
            EyeGesturesTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    // Verificar permisos antes de mostrar la app
                    if (hasCameraPermission()) {
                        // Navegación principal con NavHost
                        EyeGesturesNavigation()
                    } else {
                        // Mostrar pantalla de solicitud de permisos
                        PermissionScreen(
                            onRequestPermission = {
                                requestPermissionLauncher.launch(Manifest.permission.CAMERA)
                            }
                        )
                    }
                }
            }
        }
    }
    
    private fun hasCameraPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.CAMERA
        ) == PackageManager.PERMISSION_GRANTED
    }
}

@Composable
fun EyeGesturesTheme(content: @Composable () -> Unit) {
    MaterialTheme {
        content()
    }
}

/**
 * Configuración de navegación con NavHost
 * Gestiona la navegación entre MenuScreen, LabyrinthScreen y SnakeScreen
 */
@Composable
fun EyeGesturesNavigation() {
    // NavController para gestionar la navegación
    val navController = rememberNavController()
    
    // NavHost define todas las rutas y composables
    NavHost(
        navController = navController,
        startDestination = Screen.Menu.route,
        modifier = Modifier.fillMaxSize()
    ) {
        // PANTALLA DE MENÚ (inicio)
        composable(route = Screen.Menu.route) {
            MenuScreen(
                onNavigateToMaze = {
                    navController.navigate(Screen.Labyrinth.route)
                },
                onNavigateToSnake = {
                    navController.navigate(Screen.Snake.route)
                },
                onNavigateToCalibration = {
                    navController.navigate(Screen.Calibration.route)
                }
            )
        }
        
        // PANTALLA DEL LABERINTO
        composable(route = Screen.Labyrinth.route) {
            LabyrinthScreen(
                onBack = {
                    navController.popBackStack()
                }
            )
        }
        
        // PANTALLA DE SNAKE
        composable(route = Screen.Snake.route) {
            SnakeScreen(
                onBack = {
                    navController.popBackStack()
                }
            )
        }
        
        // PANTALLA DE CALIBRACIÓN
        composable(route = Screen.Calibration.route) {
            CalibrationScreen(
                onCalibrationComplete = { _ ->
                    // Guardar puntos de calibración
                    // TODO: Guardar en ViewModel o SharedPreferences
                    // Por ahora, solo navegar de vuelta al menú
                    navController.popBackStack(Screen.Menu.route, inclusive = false)
                },
                onBack = {
                    navController.popBackStack()
                }
            )
        }
    }
}

@Composable
fun PermissionScreen(onRequestPermission: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "📷",
            style = MaterialTheme.typography.displayLarge
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "Permiso de Cámara Requerido",
            style = MaterialTheme.typography.headlineMedium
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Esta app necesita acceso a la cámara para detectar gestos oculares",
            style = MaterialTheme.typography.bodyMedium
        )
        Spacer(modifier = Modifier.height(24.dp))
        Button(onClick = onRequestPermission) {
            Text("Conceder Permiso")
        }
    }
}
