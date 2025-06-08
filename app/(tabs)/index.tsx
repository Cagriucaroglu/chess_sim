import { ThemedText } from '@/components/ThemedText';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from "expo-router";
import { useState } from 'react';
import { ActivityIndicator, Alert, Button, Image, Modal, StyleSheet, Text, TextInput, View } from 'react-native';

export default function HomeScreen() {

    const router = useRouter();

    const [moveStringWhite, setMoveStringWhite] = useState("e4 e5 Nf3 Nc6 Bc4 Nd4 Nxe5 Qg5 Nxf7 Qxg2 Rf1 Qxe4+ Be2 Nf3#");
    const [moveStringBlack, setMoveStringBlack] = useState("e4 e5 Nf3 Nc6 Bc4 Nd4 Nxe5 Qg5 Nxf7 Qxg2 Rf1 Qxe4+ Be2 Nf3#")
    const [whitePlayer, setWhitePlayer] = useState<string>(""); // Beyaz oyuncu adı
    const [blackPlayer, setBlackPlayer] = useState<string>(""); // Siyah oyuncu adı

    const [isWhiteModalVisible, setWhiteModalVisible] = useState<boolean>(false);
    const [isBlackModalVisible, setBlackModalVisible] = useState<boolean>(false);

    const [tempPhotoResult, setTempPhotoResult] = useState<string>("");
    const [isLoading, setIsLoading] = useState(false);

    const styles = StyleSheet.create({
        body: {
            display: "flex",
            alignItems: "center",
            flexDirection: "column"
        },
        titleContainer: {
            paddingVertical: 16,
            paddingHorizontal: 8,
            alignItems: "center",
            backgroundColor: "#F2F2F2",
            borderRadius: 8,
            marginBottom: 16,
            shadowColor: "#000",
            shadowOffset: { width: 0, height: 2 },
            shadowOpacity: 0.1,
            shadowRadius: 4,
            elevation: 2,
        },
        stepContainer: {
            padding: 16,
            backgroundColor: "#FFF",
            borderRadius: 8,
            marginBottom: 16,
            shadowColor: "#000",
            shadowOffset: { width: 0, height: 2 },
            shadowOpacity: 0.1,
            shadowRadius: 4,
            elevation: 2,
        },
        stepContainer2: {
            display: "flex",
            flexDirection: "row",
            gap: 10,
            padding: 16,
            backgroundColor: "#669999",
            borderRadius: 8,
            marginBottom: 16,
            shadowColor: "#000",
            shadowOffset: { width: 0, height: 2 },
            shadowOpacity: 0.1,
            shadowRadius: 4,
            elevation: 2,
        },
        reactLogo: {
            height: 360,
            width: 360,
            top: 5,
            bottom: 0,
            left: 0,
        },
        logobackground: {
            alignItems: "center",
            height: 360,
            backgroundColor: "#EDEDBB",
            width: "100%"
        },
        detectedGameText: {
            fontSize: 16,
            fontWeight: "bold",  // Yazıyı kalınlaştırdık
            color: "#333",        // Metin rengi
        },
        modalOverlay: {
            flex: 1,
            backgroundColor: 'rgba(0,0,0,0.3)',
            justifyContent: 'center',
            alignItems: 'center',
        },
        modalContent: {
            width: '85%',
            backgroundColor: 'white',
            borderRadius: 8,
            padding: 20,
            shadowColor: '#000',
            shadowOpacity: 0.2,
            shadowRadius: 10,
            elevation: 5,
        },
        modalTitle: {
            fontSize: 18,
            marginBottom: 12,
            textAlign: 'center',
            fontWeight: '600',
        },
        input: {
            borderWidth: 1,
            borderColor: '#bbb',
            borderRadius: 6,
            paddingHorizontal: 10,
            paddingVertical: 8,
            marginBottom: 15,
            fontSize: 16,
        },
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

    });

    const startPhotoFlow = async () => {
        const whiteResult = await takePhoto();
        if (!whiteResult) return;
        setTempPhotoResult(whiteResult);
        setWhiteModalVisible(true);
    }

    const onTakeBlackPhoto = async () => {
        console.log("isloading true");
        const blackResult = await takePhoto();
        if (!blackResult) return;
        setTempPhotoResult(blackResult);
    }

    const takePhoto = async (): Promise<string | null> => {
        try {
            console.log("take photo");
            const { status } = await ImagePicker.requestCameraPermissionsAsync();
            if (status !== 'granted') {
                alert('Kamera izni verilmedi');
                return null;
            }

            const result = await ImagePicker.launchCameraAsync({
                allowsEditing: true,
                aspect: [4, 3],
                quality: 1
            });
            setIsLoading(true);
            if (!result.canceled && result.assets.length > 0) {
                const photo = result.assets[0];
                console.log("Seçilen foto:", photo.uri);

                const formData = new FormData();
                formData.append('file', {
                    uri: photo.uri,
                    name: 'chess_photo.jpg',
                    type: "image/jpeg",
                } as any);
                const response = await fetch("http://192.168.1.161:9999/analyze-chess", { //http://192.168.1.161:9999/analyze-chess
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                console.log("API cevabı:", data);
                const moves = data.message.join(" ");
                return moves;
            }
            return null
        }
        catch (err) {
            console.error('API çağrısı hatası:', err);
            Alert.alert('Hata', 'Hamle analizi sırasında bir sorun oluştu.');
            return null;
        } finally {
            console.log("isloading false")
            setIsLoading(false);  // İşlem bitince loader'ı kapat
        }
    }

    const onWhiteModalSubmit = () => {
        if (!whitePlayer.trim()) {
            Alert.alert('Uyarı', 'Lütfen beyaz oyuncunun adını gir.');
            return;
        }
        setMoveStringWhite(tempPhotoResult);
        setTempPhotoResult("");
        setWhiteModalVisible(false);
        setBlackModalVisible(true);
    }

    const onBlackModalSubmit = () => {
        if (!blackPlayer.trim()) {
            Alert.alert("Uyarı", "Lütfen siyah oyuncunun adını girin");
            return;
        }
        setMoveStringBlack(tempPhotoResult);
        setTempPhotoResult("");
        setBlackModalVisible(false);
        router.push({
            pathname: "/simulate",
            params: {
                moves: moveStringWhite,
                moves2: moveStringBlack,
                whitePlayer,
                blackPlayer
            },
        })
    }

    return (
        <View style={styles.body}>
            <View style={styles.logobackground}>
                <Image
                    source={require('@/assets/images/logo.png')}
                    style={styles.reactLogo}
                />
            </View>
            <View style={styles.titleContainer}>
                <ThemedText type="title">Chess Simulation!</ThemedText>
            </View>
            <View style={styles.stepContainer2}>
                <Button
                    title="Hamle Kağıtlarını Al ve Simüle Et"
                    onPress={startPhotoFlow}
                />
                {/* <Button
                    title="Go Simulate"
                    onPress={() =>
                        router.push({
                            pathname: "/simulate",
                            params: { moves: moveStringWhite },
                        })
                    }
                /> */}
                {
                    !isLoading ?
                        <Modal
                            visible={isWhiteModalVisible}
                            animationType='slide'
                            transparent={true}
                            onRequestClose={() => setWhiteModalVisible(false)}
                        >
                            <View style={styles.modalOverlay}>
                                <View style={styles.modalContent}>
                                    <Text style={styles.modalTitle}>Beyaz Oyuncunun Adı</Text>
                                    <TextInput
                                        style={styles.input}
                                        placeholder="Beyaz oyuncunun adını gir"
                                        value={whitePlayer}
                                        onChangeText={setWhitePlayer}
                                    />
                                    <Button
                                        title="Kaydet & Sonraki: Siyah'ın Hamle Kağıdı"
                                        onPress={onWhiteModalSubmit}
                                    />
                                </View>
                            </View>
                        </Modal> :
                        <Modal transparent={true} animationType="fade" visible={isLoading}>
                            <View style={styles.loaderOverlay}>
                                <View style={styles.loaderBox}>
                                    <ActivityIndicator size="large" color="#000" />
                                    <Text style={{ marginTop: 10 }}>Fotoğraf işleniyor...</Text>
                                </View>
                            </View>
                        </Modal>
                }

                {
                    !isLoading ?
                        <Modal
                            visible={isBlackModalVisible}
                            animationType='slide'
                            transparent={true}
                            onRequestClose={() => setBlackModalVisible(false)}
                        >
                            <View style={styles.modalOverlay}>
                                <View style={styles.modalContent}>
                                    <Text style={styles.modalTitle}>Siyahın Hamle Kağıdını işle</Text>
                                    <Button
                                        title="Siyahın Hamle Kağıdını Fotoğraflayın"
                                        onPress={onTakeBlackPhoto}
                                    />
                                    {tempPhotoResult ? (
                                        <>
                                            <Text style={[styles.modalTitle, { marginTop: 20 }]}>
                                                Siyah Oyuncunun Adı
                                            </Text>
                                            <TextInput
                                                style={styles.input}
                                                placeholder='Siyah Oyuncunun Adını gir'
                                                value={blackPlayer}
                                                onChangeText={setBlackPlayer}
                                            />
                                            <Button
                                                title='Tamamla ve Simüle Et'
                                                onPress={onBlackModalSubmit}
                                            />
                                        </>
                                    ) : null}
                                </View>
                            </View>
                        </Modal>
                        :
                        <Modal transparent={true} animationType="fade" visible={isLoading}>
                            <View style={styles.loaderOverlay}>
                                <View style={styles.loaderBox}>
                                    <ActivityIndicator size="large" color="#000" />
                                    <Text style={{ marginTop: 10 }}>Fotoğraf işleniyor...</Text>
                                </View>
                            </View>
                        </Modal>
                }

            </View>
            <View style={styles.stepContainer}>
                <Text style={styles.detectedGameText}>Detected Game:  {moveStringWhite}</Text>
            </View>
        </View>
    );
}


