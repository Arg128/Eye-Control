import React from 'react';
import { View, Text, Button } from 'react-native';
import { useNavigation } from '@react-navigation/native';

const HomeScreen = () => {
    const navigation = useNavigation();

    const handleCalibration = () => {
        navigation.navigate('Calibration');
    };

    return (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
            <Text style={{ fontSize: 24, marginBottom: 20 }}>Welcome to Eye Control</Text>
            <Button title="Start Calibration" onPress={handleCalibration} />
        </View>
    );
};

export default HomeScreen;