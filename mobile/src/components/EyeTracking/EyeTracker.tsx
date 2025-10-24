import React, { useEffect, useRef } from 'react';
import { View, Text } from 'react-native';
import { detectEyes } from '../../services/eyeDetection';

const EyeTracker = () => {
    const videoRef = useRef(null);

    useEffect(() => {
        const startEyeTracking = async () => {
            if (videoRef.current) {
                // Initialize eye tracking logic here
                await detectEyes(videoRef.current);
            }
        };

        startEyeTracking();

        return () => {
            // Cleanup logic if necessary
        };
    }, []);

    return (
        <View>
            <Text>Eye Tracker Component</Text>
            <video ref={videoRef} style={{ display: 'none' }} />
        </View>
    );
};

export default EyeTracker;