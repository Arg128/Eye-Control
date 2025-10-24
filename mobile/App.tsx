import React from 'react';
import {
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  View,
} from 'react-native';

function App(): React.JSX.Element {
  return (
    <>
      <StatusBar barStyle="dark-content" />
      <ScrollView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>🎯 Eye Control Mobile</Text>
          <Text style={styles.subtitle}>React Native Running!</Text>
          <View style={styles.card}>
            <Text style={styles.cardTitle}>✅ Setup Complete</Text>
            <Text style={styles.cardText}>Your app works!</Text>
          </View>
        </View>
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 24,
    minHeight: 600,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    color: '#666',
    marginBottom: 32,
  },
  card: {
    backgroundColor: '#4CAF50',
    borderRadius: 12,
    padding: 20,
    marginTop: 20,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  cardText: {
    fontSize: 16,
    color: '#fff',
  },
});

export default App;