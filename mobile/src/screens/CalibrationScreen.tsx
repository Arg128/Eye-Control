import React, { useEffect } from 'react';
import { View, Text, Button } from 'react-native';
import EyeTracker from '../components/EyeTracking/EyeTracker';
import { startCalibration, stopCalibration } from '../services/eyeDetection';

const CalibrationScreen = () => {
    useEffect(() => {
        startCalibration();

        return () => {
            stopCalibration();
        };
    }, []);

    return (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
            <Text>Calibración del Seguimiento Ocular</Text>
            <EyeTracker />
            <Button title="Iniciar Calibración" onPress={startCalibration} />
            <Button title="Detener Calibración" onPress={stopCalibration} />
        </View>
    );
};

export default CalibrationScreen;