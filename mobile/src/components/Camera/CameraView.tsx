import React, { useEffect, useRef } from 'react';
import { View, StyleSheet } from 'react-native';
import { RNCamera } from 'react-native-camera';

const CameraView = () => {
    const cameraRef = useRef<RNCamera>(null);

    useEffect(() => {
        const checkCameraPermission = async () => {
            const { status } = await RNCamera.requestPermissionsAsync();
            if (status !== 'granted') {
                console.error('Camera permission not granted');
            }
        };

        checkCameraPermission();
    }, []);

    return (
        <View style={styles.container}>
            <RNCamera
                ref={cameraRef}
                style={styles.camera}
                type={RNCamera.Constants.Type.back}
                flashMode={RNCamera.Constants.FlashMode.off}
                onCameraReady={() => {
                    console.log('Camera is ready');
                }}
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    camera: {
        flex: 1,
        width: '100%',
    },
});

export default CameraView;