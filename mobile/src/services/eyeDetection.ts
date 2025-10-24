import { useEffect, useState } from 'react';
import { Camera } from 'expo-camera';
import * as tf from '@tensorflow/tfjs';
import { fetch } from 'react-native-fetch';

const MODEL_URL = 'https://your-model-url/model.json';

export const useEyeDetection = () => {
    const [model, setModel] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadModel = async () => {
            try {
                const loadedModel = await tf.loadGraphModel(MODEL_URL);
                setModel(loadedModel);
            } catch (err) {
                setError(err);
            } finally {
                setIsLoading(false);
            }
        };

        loadModel();
    }, []);

    const detectEyes = async (imageData) => {
        if (!model) {
            throw new Error('Model not loaded');
        }

        const tensor = tf.browser.fromPixels(imageData);
        const predictions = await model.predict(tensor.expandDims(0)).data();
        return predictions;
    };

    return { model, isLoading, error, detectEyes };
};