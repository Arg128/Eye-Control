package com.example.eyegestures

import androidx.compose.ui.geometry.Offset

/**
 * Smoothing buffer for gaze coordinates using moving average.
 * Implements the same buffering strategy as the web project.
 */
class SmoothingBuffer(private val maxSize: Int = 20) {
    private val buffer = mutableListOf<Offset>()
    
    /**
     * Add a new point to the buffer
     */
    fun push(x: Float, y: Float) {
        buffer.add(Offset(x, y))
        
        // Remove oldest point if buffer exceeds max size
        if (buffer.size > maxSize) {
            buffer.removeAt(0)
        }
    }
    
    /**
     * Get the smoothed (averaged) position from buffer
     * Returns null if buffer is empty
     */
    fun getSmoothed(): Offset? {
        if (buffer.isEmpty()) return null
        
        // Calculate average of all points in buffer
        val sumX = buffer.sumOf { it.x.toDouble() }.toFloat()
        val sumY = buffer.sumOf { it.y.toDouble() }.toFloat()
        
        return Offset(
            x = sumX / buffer.size,
            y = sumY / buffer.size
        )
    }
    
    /**
     * Get the last raw (unsmoothed) point
     */
    fun getLast(): Offset? = buffer.lastOrNull()
    
    /**
     * Clear all buffered points
     */
    fun clear() {
        buffer.clear()
    }
    
    /**
     * Get current buffer size
     */
    fun size(): Int = buffer.size
    
    /**
     * Check if buffer has enough samples for reliable smoothing
     */
    fun isReady(): Boolean = buffer.size >= (maxSize / 2)
}
