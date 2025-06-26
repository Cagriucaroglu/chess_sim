import { ThemedText } from '@/components/ThemedText';
import Constants from 'expo-constants';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from "expo-router";
import { useState } from 'react';
import { ActivityIndicator, Alert, Button, Dimensions, Image, Modal, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

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
    const { height, width } = Dimensions.get("window");
    const HEADER_HEIGHT = 619.2; // üstteki sabit yükseklikler
    const tableHeight = height - HEADER_HEIGHT;

    const API_URL = Constants.expoConfig?.extra?.apiUrl;


    const styles = StyleSheet.create({
        tableWrapper: {
            flexDirection: 'row',
            justifyContent: 'space-between',
            padding: 10,    
        },
        columnBlock: {
            flex: 1,
            marginHorizontal: 5,
        },
        tableScroll: {
            height: tableHeight, // Sabit yükseklik
            width: width - 15,
            borderWidth: 1,
            borderColor: '#ccc',
            borderRadius: 8,
            margin: 10,
        },
        scrollContent: {
            padding: 10,
        },
        tableHeaderRow: {
            flexDirection: 'row',
            backgroundColor: "#e3f2fd", // burada renk eklendi
            paddingVertical: 6,
        },
        tableRow: {
            flexDirection: 'row',
            paddingVertical: 4,
            borderBottomWidth: 1,
            borderColor: '#ddd',
        },
        headerCell: {
            flex: 1,
            fontWeight: 'bold',
            textAlign: 'center',
        },
        cell: {
            flex: 1,
            textAlign: 'center',
        },
        body: {
            display: "flex",
            alignItems: "center",
            flexDirection: "column",
            backgroundColor: "#e3f2fd", // burada renk eklendi
        },
        titleContainer: {
            marginTop: 10,
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
            flexDirection: "row",
            justifyContent: "space-around",
            alignItems: "center",
            flexWrap: "wrap",
            padding: 20,
            backgroundColor: "#e0f7fa",
            borderRadius: 16,
            marginBottom: 20,
            shadowColor: "#000",
            shadowOffset: { width: 0, height: 4 },
            shadowOpacity: 0.15,
            shadowRadius: 6,
            elevation: 3,
        },
        reactLogo: {
            height: 300,
            width:  300,
            top: 5,
            bottom: 0,
            left: 0,
        },
        logobackground: {
            alignItems: "center",
            height: 300,
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
            width: '90%',
            backgroundColor: '#fefefe',
            borderRadius: 12,
            padding: 24,
            shadowColor: '#333',
            shadowOffset: { width: 0, height: 4 },
            shadowOpacity: 0.3,
            shadowRadius: 8,
            elevation: 6,
        },
        customButton: {
            backgroundColor: "#00796b",
            paddingVertical: 12,
            paddingHorizontal: 20,
            borderRadius: 10,
            marginTop: 10,
        },
        customButtonText: {
            color: "white",
            fontSize: 16,
            fontWeight: "600",
            textAlign: "center",
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

    const parseMovesToDoubleColumn = (moveStr: string) => {
        const moves = moveStr.trim().split(" ");
        const result = [];

        for (let i = 0; i < moves.length; i += 2) {
            result.push({
                moveNo: i / 2 + 1,
                white: moves[i],
                black: moves[i + 1] || "-",
            });
        }

        // Sol blok: ilk 20 hamle, sağ blok: sonraki 20 hamle
        const left = result.slice(0, 20);
        const right = result.slice(20, 40); // 40 hamleye kadar gösterecek

        return { left, right };
    };

    const { left, right } = parseMovesToDoubleColumn(moveStringWhite);

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
                const response = await fetch(`${API_URL}/analyze-chess`, { //http://192.168.1.161:9999/analyze-chess
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
                <ThemedText type="title">Chess Simulation</ThemedText>
            </View>
            <View style={styles.stepContainer2}>
                <TouchableOpacity style={styles.customButton} onPress={startPhotoFlow}>
                    <Text style={styles.customButtonText}>Hamle Kağıtlarını Al ve Simüle Et</Text>
                </TouchableOpacity>
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
                                    <TouchableOpacity style={styles.customButton} onPress={onWhiteModalSubmit}>
                                        <Text style={styles.customButtonText}>Kaydet & Sonraki: Siyah'ın Hamle Kağıdı</Text>
                                    </TouchableOpacity>
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
                                            <TouchableOpacity style={styles.customButton} onPress={onBlackModalSubmit}>
                                                <Text style={styles.customButtonText}>Tamamla ve Simüle Et</Text>
                                            </TouchableOpacity>
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
            <Text>Detected Game: {API_URL}</Text>
            <ScrollView style={styles.tableScroll} contentContainerStyle={styles.scrollContent}>
                <View style={styles.tableWrapper}>
                    <View style={styles.columnBlock}>
                        <View style={styles.tableHeaderRow}>
                            <Text style={styles.headerCell}>No.</Text>
                            <Text style={styles.headerCell}>White</Text>
                            <Text style={styles.headerCell}>Black</Text>
                        </View>
                        {left.map((row, index) => (
                            <View style={styles.tableRow} key={`left-${index}`}>
                                <Text style={styles.cell}>{row.moveNo}</Text>
                                <Text style={styles.cell}>{row.white}</Text>
                                <Text style={styles.cell}>{row.black}</Text>
                            </View>
                        ))}
                    </View>
                    {
                        right.length > 0 &&
                        <View style={styles.columnBlock}>
                            <View style={styles.tableHeaderRow}>
                                <Text style={styles.headerCell}>No.</Text>
                                <Text style={styles.headerCell}>White</Text>
                                <Text style={styles.headerCell}>Black</Text>
                            </View>
                            {right.map((row, index) => (
                                <View style={styles.tableRow} key={`right-${index}`}>
                                    <Text style={styles.cell}>{row.moveNo + 20}</Text>
                                    <Text style={styles.cell}>{row.white}</Text>
                                    <Text style={styles.cell}>{row.black}</Text>
                                </View>
                            ))}
                        </View>
                    }
                </View>
            </ScrollView>

        </View>
    );
}


