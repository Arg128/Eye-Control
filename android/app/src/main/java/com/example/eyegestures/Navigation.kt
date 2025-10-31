package com.example.eyegestures

/**
 * Rutas de navegación para la aplicación
 * Define las diferentes pantallas y sus argumentos
 */
object NavigationRoutes {
    const val MENU = "menu"
    const val SNAKE = "snake"
    const val LABYRINTH = "labyrinth"
    const val CALIBRATION = "calibration"
}

/**
 * Sealed class para navegación type-safe
 * Previene errores de tipado en las rutas
 */
sealed class Screen(val route: String) {
    object Menu : Screen(NavigationRoutes.MENU)
    object Snake : Screen(NavigationRoutes.SNAKE)
    object Labyrinth : Screen(NavigationRoutes.LABYRINTH)
    object Calibration : Screen(NavigationRoutes.CALIBRATION)
}
