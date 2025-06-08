import React from 'react';
import { ActivityIndicator, Modal, StyleSheet, Text, View } from 'react-native';

const styles = StyleSheet.create({
            loaderOverlay: {
            flex: 1,
            backgroundColor: 'rgba(0,0,0,0.3)',
            justifyContent: 'center',
            alignItems: 'center',
        },
        loaderBox: {
            backgroundColor: '#fff',
            padding: 20,
            borderRadius: 10,
            alignItems: 'center',
        },
})

interface ILoaderprop {
    isLoading: boolean;
}

export default function Loader({isLoading} : ILoaderprop) {
        return (
            <Modal transparent={true} animationType="fade" visible={isLoading}>
                <View style={styles.loaderOverlay}>
                    <View style={styles.loaderBox}>
                        <ActivityIndicator size="large" color="#000" />
                        <Text style={{ marginTop: 10 }}>Fotoğraf işleniyor...</Text>
                    </View>
                </View>
            </Modal>
        )    
}
