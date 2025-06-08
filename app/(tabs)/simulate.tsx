import { Dimensions, Image, ImageBackground, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { Chess } from "chess.js";
import { useLocalSearchParams } from "expo-router";
import React, { useEffect, useState } from 'react';
import Chessboard from '../components/chessboard';
import { CheckedProvider } from '../providers/CheckedContext';
import { findCheckingPieces, findKingSquare } from '../providers/FindKingSquare';


export default function TabTwoScreen() {

    const { moves, moves2, blackPlayer, whitePlayer } = useLocalSearchParams<{ moves: string, moves2: string, whitePlayer: string, blackPlayer: string }>();
    const backgroundImage = require('../../assets/images/background.png')
    const whiteplayerImage = require('../../assets/images/white.png')
    const blackplayerImage = require('../../assets/images/black.png')


    const [position, setPosition] = useState("start");
    const [currentMove, setCurrentMove] = useState(0);
    const [game, setGame] = useState(new Chess());
    const [capturedByWhite, setCapturedByWhite] = useState<string[]>([]);
    const [capturedByBlack, setCapturedByBlack] = useState<string[]>([]);
    const [isthereanyillegal, setIsthereanyillegal] = useState(false);
    const [checkedSquare, setCheckedSquare] = useState("");
    const [checkingSquare, setCheckingSquare] = useState("");
    const [gameResult, seGameResult] = useState<string | null>();

    const movesArray = moves?.split(/\s+/) ?? [];
    const movesArray2 = moves2?.split(/\s+/) ?? [];
    const { width } = Dimensions.get("window");
    const title = "CHESS - SIM"

    useFocusEffect(
        React.useCallback(() => {
            resetGame();
        }, [moves, moves2, whitePlayer, blackPlayer])
    );

    const styles = StyleSheet.create({
        header: {
            fontSize: 26, // Yazı boyutunu istediğiniz gibi ayarlayabilirsiniz
            fontWeight: 'bold', // Opsiyonel: kalın yapar
            justifyContent: 'center',
            textAlign: 'center',       // Yatayda ortalar
            alignSelf: 'center',
            marginTop: 50,             // Sayfanın üstünden boşluk (duruma göre ayarlayabilirsin)

        },
        titleContainer: {
            flexDirection: 'row',
            gap: 8,
        },
        nextmovebutton: {
            backgroundColor: "#77bd89",
            borderRadius: 5,
            padding: 5,
            width: ((width / 2) - 10),
            alignItems: "center"
        },
        movesContainer: {
            display: "flex",
            flexDirection: "row",
            gap: 10,
            marginTop: 15
        },
        userNamesContainer: {
            display: "flex",
            flexDirection: "row",
            gap: 10,
            alignItems: "center"
        },
        capturedpiecescontainer: {
            display: "flex",
            flexDirection: "row",
            gap: 10,
            marginTop: 15,
            justifyContent: "space-between",
        },
        titleandboardcontainer: {
            display: "flex",
            flexDirection: "column",
            gap: 20,
            alignItems: "center",
            justifyContent: "center"
        },
        // reloadıcon: {
        //     position: "relative",
        //     left: 0,
        //     top: 50
        // },
        capturedpieces: {
            display: "flex",
            flexDirection: "row",
            gap: 2,
            width: width / 2,
            minHeight: 40,
            flexWrap: "wrap",
        },
        reloadandillegalmove: {
            position: "relative",
            left: 0,
            top: 20,
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "center"
        }
    });

    useEffect(() => {
        setPosition(game.fen());
    }, [game]);

    useEffect(() => {
        resetGame();
    }, [])

    const playNextMove = () => {
        let movestr = movesArray[currentMove];
        let isnextmovelegal = isMoveLegal(movestr);
        if (!isnextmovelegal && !gameResult) {
            movestr = movesArray2[currentMove];
            isnextmovelegal = isMoveLegal(movestr);
        }

        if (currentMove < movesArray.length && isnextmovelegal) {
            const move = game.move(movestr);
            if (game.inCheck()) {
                setCheckedSquare(findKingSquare(game, game.turn()));
                setCheckingSquare(findCheckingPieces(movestr));
            }
            else {
                setCheckedSquare("");
                setCheckingSquare("");
            }
            setPosition(game.fen());
            setCurrentMove(currentMove + 1);
            if (move.captured) {
                if (move.color === 'w') {
                    setCapturedByWhite([...capturedByWhite, move.captured]);
                } else {
                    setCapturedByBlack([...capturedByBlack, move.captured]);
                }
            }
            if (game.isGameOver()) {
                if (game.inCheck()) {
                    const winner = game.turn() === 'w' ? 'Siyahlar' : 'Beyazlar';
                    seGameResult(`${winner} kazandı 🏆`);
                }
                else if (game.isDraw()) {
                    seGameResult('Oyun berabere 🤝');
                }
            }
        }
        if (!isnextmovelegal && !gameResult)
            setIsthereanyillegal(true);

        else if (!gameResult)
            setIsthereanyillegal(false);
    };

    const playPreviousMove = () => {
        if (currentMove > 0) {
            const newGame = new Chess();
            setCapturedByBlack([]);
            setCapturedByWhite([]);
            setCheckedSquare("");
            setCheckingSquare("");
            seGameResult(null);
            setIsthereanyillegal(false);
            for (let i = 0; i < currentMove - 1; i++) {
                const move = newGame.move(movesArray[i])
                if (move.captured) {
                    if (move.color = "w") {
                        setCapturedByWhite([...capturedByWhite, move.captured]);
                    }
                    else {
                        setCapturedByBlack([...capturedByBlack, move.captured])
                    }
                }
            }
            setGame(newGame);
            setPosition(newGame.fen());
            setCurrentMove(currentMove - 1);
        }
    }

    const isMoveLegal = (moveStr: string) => {
        const moves = game.moves();
        return moves.includes(moveStr);
    }

    const pieceImages: Record<string, { w: any; b: any }> = {
        p: {
            w: require('../../assets/chesspieces/wp.png'),
            b: require('../../assets/chesspieces/bp.png'),
        },
        n: {
            w: require('../../assets/chesspieces/wn.png'),
            b: require('../../assets/chesspieces/bn.png'),
        },
        b: {
            w: require('../../assets/chesspieces/wb.png'),
            b: require('../../assets/chesspieces/bb.png'),
        },
        r: {
            w: require('../../assets/chesspieces/wr.png'),
            b: require('../../assets/chesspieces/br.png'),
        },
        q: {
            w: require('../../assets/chesspieces/wq.png'),
            b: require('../../assets/chesspieces/bq.png'),
        },
        k: {
            w: require('../../assets/chesspieces/wk.png'),
            b: require('../../assets/chesspieces/bk.png'),
        },
    };


    const resetGame = () => {
        const newGame = new Chess();
        setGame(newGame);
        setPosition(newGame.fen());
        setCurrentMove(0);
        setCapturedByWhite([]);
        setCapturedByBlack([]);
        setIsthereanyillegal(false);
        setCheckedSquare("");
        setCheckingSquare("");
        seGameResult(null);
    }

    useEffect(() => {
        console.log("FEN güncellendi:", position);
    }, [position]);

    return (
        <ImageBackground source={backgroundImage} style={{ flex: 1 }}>
            <Text style={styles.header}>
                {title}
            </Text>
            <View style={styles.capturedpiecescontainer}>
                <View style={styles.userNamesContainer}>
                    <Image
                        source={blackplayerImage}
                        resizeMode="contain"
                    />
                    <Text>{blackPlayer}</Text>
                </View>
                <View style={styles.userNamesContainer}>
                    <Image
                        source={whiteplayerImage}
                        resizeMode="contain"
                    />
                    <Text>{whitePlayer}</Text>
                </View>
            </View>
            <View style={styles.capturedpiecescontainer}>
                <Text style={{ fontSize: 15 }}>Captured By Black:</Text>
                <Text style={{ fontSize: 15 }}>Captured By White:</Text>
            </View>
            <View style={styles.capturedpiecescontainer}>
                <View style={styles.capturedpieces}>
                    {capturedByBlack.map((piece, index) => (
                        <Image
                            key={index}
                            source={pieceImages[piece.toLowerCase()].w}
                            style={{ width: 24, height: 24 }}
                        />
                    ))}
                </View>
                <View style={styles.capturedpieces}>
                    {capturedByWhite.map((piece, index) => (
                        <Image
                            key={index}
                            source={pieceImages[piece.toLowerCase()].b}
                            style={{ width: 24, height: 24 }}
                        />
                    ))}
                </View>
            </View>

            <View style={styles.reloadandillegalmove}>
                <TouchableOpacity onPress={resetGame} style={{ position: "absolute", left: 0 }}>
                    <Ionicons name="reload" size={28} color="black" />
                </TouchableOpacity>
                <Text style={{ color: '#f5f5f5', fontSize: 20 }}>
                    {isthereanyillegal && `Geçersiz Hamle: ${movesArray[currentMove]}`}
                    {gameResult && gameResult}
                </Text>
            </View>
            <View style={{ flex: 1, alignItems: "center", gap: 10, marginTop: 35 }}>
                <CheckedProvider CheckedSquare={checkedSquare} CheckingSquare={checkingSquare}>
                    <Chessboard fen={position} />
                </CheckedProvider>
                <View style={styles.movesContainer}>
                    <TouchableOpacity style={styles.nextmovebutton} onPress={playPreviousMove}>
                        <Text>{"Back Move"}</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.nextmovebutton} onPress={playNextMove}>
                        <Text>{"Next Move"}</Text>
                    </TouchableOpacity>
                </View>
                {/* <Button title="Next Move" onPress={playNextMove} color={"#77bd89"} /> */}
                {/* <TextInput>
                {moves}
            </TextInput> */}
            </View>
        </ImageBackground>
    );
}

//  renderPiece={(piece: string) => {
//                 console.log("Render edilen parça:", piece, pieceImages[piece]);
//                 return (                
//                     <Image 
//                         source={pieceImages[piece]}
//                         resizeMode='contain'
//                         style={{width: 350/8, height: 350/8}}
//                     /> 
//                 )}               
//             }

