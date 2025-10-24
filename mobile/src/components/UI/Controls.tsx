import React from 'react';
import { View, Button, StyleSheet } from 'react-native';

const Controls = ({ onStartTracking, onStopTracking }) => {
    return (
        <View style={styles.container}>
            <Button title="Start Tracking" onPress={onStartTracking} />
            <Button title="Stop Tracking" onPress={onStopTracking} />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        padding: 20,
    },
});

export default Controls;